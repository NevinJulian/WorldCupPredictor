"""Unit tests on synthetic data — no network needed. Run: `pytest -q`

These guard the two things most easily broken: Elo correctness and as-of (no-leakage) features.
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import clean, datasets, elo, features, tournament  # noqa: E402


def _synthetic_results(n_per_pair: int = 6) -> pd.DataFrame:
    """A small round-robin-ish history among 4 teams with fixed dates."""
    teams = ["A", "B", "C", "D"]
    rng = np.random.default_rng(42)
    rows, date = [], pd.Timestamp("2000-01-01")
    for _ in range(n_per_pair):
        for h in teams:
            for a in teams:
                if h == a:
                    continue
                date += pd.Timedelta(days=7)
                hs, as_ = int(rng.integers(0, 4)), int(rng.integers(0, 4))
                rows.append({
                    "date": date, "home_team": h, "away_team": a,
                    "home_score": hs, "away_score": as_,
                    "tournament": "Friendly", "city": "X", "country": "X", "neutral": False,
                })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Elo
# --------------------------------------------------------------------------- #
def test_goal_diff_multiplier():
    assert elo.goal_diff_multiplier(1) == 1.0
    assert elo.goal_diff_multiplier(2) == 1.5
    assert elo.goal_diff_multiplier(3) == 1.75
    assert elo.goal_diff_multiplier(5) == pytest.approx(1.75 + 2 / 8)


def test_k_for_tournament():
    assert elo.k_for_tournament("Friendly") == elo.K_FRIENDLY
    assert elo.k_for_tournament("FIFA World Cup") == elo.K_WORLD_CUP
    assert elo.k_for_tournament("FIFA World Cup qualification") == elo.K_QUALIFIER
    assert elo.k_for_tournament("UEFA Euro") == elo.K_CONTINENTAL


def test_elo_home_advantage_and_first_match():
    df = pd.DataFrame([{
        "date": pd.Timestamp("2020-01-01"), "home_team": "A", "away_team": "B",
        "home_score": 1, "away_score": 1, "tournament": "Friendly",
        "city": "x", "country": "x", "neutral": False,
    }])
    out, _ = elo.compute_elo(df)
    # Both start at default; expected home > 0.5 purely from home advantage.
    assert out.loc[0, "elo_home"] == elo.DEFAULT_RATING
    assert out.loc[0, "elo_expected_home"] > 0.5


def _varied_results() -> pd.DataFrame:
    """A short history exercising several K-tiers and goal-difference branches."""
    rows = [
        ("2018-01-01", "A", "B", 1, 0, "Friendly", False),          # margin 1, K_FRIENDLY
        ("2018-02-01", "B", "C", 3, 0, "FIFA World Cup", True),     # margin 3 (gd 1.75), neutral, K_WORLD_CUP
        ("2018-03-01", "C", "A", 2, 2, "UEFA Euro", False),         # draw, K_CONTINENTAL
        ("2018-04-01", "A", "C", 5, 1, "FIFA World Cup qualification", False),  # margin 4 (gd 1.875), K_QUALIFIER
        ("2018-05-01", "B", "A", 0, 1, "Friendly", False),          # margin 1
        ("2018-06-01", "C", "B", 4, 0, "Nations League", True),     # margin 4, neutral, K_MINOR
    ]
    return pd.DataFrame([
        {"date": pd.Timestamp(d), "home_team": h, "away_team": a, "home_score": hs,
         "away_score": as_, "tournament": t, "city": "x", "country": "x", "neutral": neu}
        for d, h, a, hs, as_, t, neu in rows
    ])


def test_compute_elo_default_params_reproduce_baseline():
    """Default (home_adv=100, k_scale=1, gd_strength=1) must reproduce the original arithmetic.

    Guards that parametrising compute_elo did not change any rating. The reference loop below
    is an independent re-implementation of the pre-parametrisation eloratings.net update.
    """
    df = _varied_results()

    def original_gd(margin: int) -> float:           # pre-parametrisation goal-diff multiplier
        m = abs(int(margin))
        if m <= 1:
            return 1.0
        if m == 2:
            return 1.5
        if m == 3:
            return 1.75
        return 1.75 + (m - 3) / 8.0

    ratings: dict[str, float] = {}
    ref_post_h, ref_post_a, ref_pre_h, ref_pre_a = [], [], [], []
    for r in df.itertuples(index=False):
        rh = ratings.get(r.home_team, elo.DEFAULT_RATING)
        ra = ratings.get(r.away_team, elo.DEFAULT_RATING)
        adv = 0.0 if r.neutral else elo.DEFAULT_HOME_ADV
        we = 1.0 / (1.0 + 10.0 ** (-(rh - ra + adv) / 400.0))
        w = 1.0 if r.home_score > r.away_score else (0.5 if r.home_score == r.away_score else 0.0)
        k = elo.k_for_tournament(r.tournament)
        delta = k * original_gd(r.home_score - r.away_score) * (w - we)
        ratings[r.home_team], ratings[r.away_team] = rh + delta, ra - delta
        ref_pre_h.append(rh); ref_pre_a.append(ra)
        ref_post_h.append(rh + delta); ref_post_a.append(ra - delta)

    out, _ = elo.compute_elo(df)   # default params
    assert out["elo_home"].to_list() == pytest.approx(ref_pre_h)
    assert out["elo_away"].to_list() == pytest.approx(ref_pre_a)
    assert out["elo_home_post"].to_list() == pytest.approx(ref_post_h)
    assert out["elo_away_post"].to_list() == pytest.approx(ref_post_a)


def test_elo_params_change_ratings():
    """The three knobs are actually wired: changing each moves ratings off the default."""
    df = _varied_results()
    base, _ = elo.compute_elo(df)
    for kwargs in ({"home_adv": 50.0}, {"k_scale": 1.5}, {"gd_strength": 0.0}):
        tuned, _ = elo.compute_elo(df, **kwargs)
        assert not np.allclose(tuned["elo_home_post"], base["elo_home_post"]), \
            f"{kwargs} did not change ratings"
    # gd_strength=1.0 with margin-1-only data is a no-op vs default on those rows is trivially true;
    # but gd_strength=0 must flatten every multiplier to 1 -> different from default here.


def test_elo_is_as_of_no_leakage():
    """A team's pre-match Elo at match k must equal its post-match Elo from match k-1."""
    res = _synthetic_results()
    out, _ = elo.compute_elo(res)
    out = out.sort_values("date").reset_index(drop=True)
    for team in ["A", "B", "C", "D"]:
        appears = out[(out.home_team == team) | (out.away_team == team)]
        prev_post = None
        for _, r in appears.iterrows():
            pre = r["elo_home"] if r["home_team"] == team else r["elo_away"]
            if prev_post is not None:
                assert pre == pytest.approx(prev_post), "Elo leaked across matches"
            prev_post = r["elo_home_post"] if r["home_team"] == team else r["elo_away_post"]


# --------------------------------------------------------------------------- #
# Features
# --------------------------------------------------------------------------- #
def test_build_features_form_is_as_of():
    res = _synthetic_results()
    res = clean.load_clean_results.__wrapped__ if hasattr(clean.load_clean_results, "__wrapped__") else None
    # Build a cleaned frame directly (bypass file IO).
    m = _synthetic_results()
    m["date"] = pd.to_datetime(m["date"])
    m["played"] = True
    m["margin"] = m["home_score"] - m["away_score"]
    m["total_goals"] = m["home_score"] + m["away_score"]
    m["result"] = np.where(m.margin > 0, "H", np.where(m.margin < 0, "A", "D"))
    m["year"] = m["date"].dt.year
    with_elo, _ = elo.compute_elo(m)
    feat = features.build_features(with_elo)

    # The very first match in the dataset has no prior games for either side -> form NaN.
    first = feat.sort_values("date").iloc[0]
    assert pd.isna(first["home_form_ppg_5"]), "form should be undefined before any match (as-of)"
    # Feature table is one row per match.
    assert len(feat) == len(m)
    # Diff columns exist.
    assert "form_ppg_5_diff" in feat.columns
    assert "elo_diff" in feat.columns


def test_feature_columns_excludes_targets():
    m = _synthetic_results()
    m["date"] = pd.to_datetime(m["date"]); m["played"] = True
    m["result"] = "H"; m["margin"] = 1; m["total_goals"] = 1; m["year"] = 2000
    with_elo, _ = elo.compute_elo(m)
    feat = features.build_features(with_elo)
    fc = features.feature_columns(feat)
    for leak in ["home_score", "away_score", "result", "margin", "total_goals"]:
        assert leak not in fc


# --------------------------------------------------------------------------- #
# Splits & simulator
# --------------------------------------------------------------------------- #
def test_time_split_is_chronological():
    m = _synthetic_results()
    m["date"] = pd.to_datetime(m["date"]); m["played"] = True
    train, test = datasets.time_split(m, "2000-03-01")
    assert train["date"].max() < pd.Timestamp("2000-03-01") <= test["date"].min()


def test_tournament_simulation_runs():
    # The simulator models the real 2026 format: 12 groups A-L of 4 (48 teams).
    teams = [f"T{i}" for i in range(48)]
    groups = pd.DataFrame({"group": [chr(ord("A") + i // 4) for i in range(48)], "team": teams})
    ratings = {t: 1500 + 5 * i for i, t in enumerate(teams)}
    model = tournament.EloMatchModel(ratings)
    odds = tournament.simulate_tournament(groups, model, n_sims=200, seed=1)
    assert len(odds) == 48
    assert (odds["advance"] <= 1.0).all() and (odds["Winner"] >= 0).all()
    assert odds["Winner"].sum() == pytest.approx(1.0, abs=0.05)   # exactly one winner per sim
    assert odds["advance"].sum() == pytest.approx(32.0, abs=1e-9)  # 32 qualifiers per sim
