"""Unit tests for the Dixon-Coles goals model. Synthetic data, no network. Run: `pytest -q`

Guards: a valid scoreline-derived H/D/A distribution, the simulator interface
(`sample_scoreline` runs inside `simulate_tournament`), graceful cold-start for unseen teams,
the low-score (rho) correction, and as-of fitting (the model never sees test-only teams).
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import models, tournament  # noqa: E402


def _history(seed: int = 0, n: int = 800, start: str = "2014-01-01"):
    """A fittable history: 8 teams with latent attack/defence, Poisson scorelines."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(8)]
    att = {t: float(rng.normal(0, 0.4)) for t in teams}
    dfc = {t: float(rng.normal(0, 0.3)) for t in teams}
    base, adv = 0.2, 0.25
    rows, date = [], pd.Timestamp(start)
    for _ in range(n):
        date += pd.Timedelta(days=3)
        h, a = rng.choice(teams, 2, replace=False)
        neutral = bool(rng.integers(0, 2))
        lam = np.exp(base + (0.0 if neutral else adv) + att[h] - dfc[a])
        mu = np.exp(base + att[a] - dfc[h])
        rows.append({
            "date": date, "home_team": h, "away_team": a,
            "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
            "neutral": neutral, "tournament": "Friendly",
        })
    df = pd.DataFrame(rows)
    df["played"] = True
    df["year"] = df["date"].dt.year
    df["result"] = np.where(df.home_score > df.away_score, "H",
                            np.where(df.home_score < df.away_score, "A", "D"))
    return df, teams, att, dfc


def _wc_frame():
    """Friendlies 2006-2009 (training pool) + a small FIFA World Cup 2010 (the test fold)."""
    df, teams, _, _ = _history(seed=3, n=300, start="2006-01-01")
    rng = np.random.default_rng(9)
    wc, rows = pd.Timestamp("2010-06-11"), []
    for _ in range(8):
        wc += pd.Timedelta(days=2)
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({
            "date": wc, "home_team": h, "away_team": a,
            "home_score": int(rng.integers(0, 4)), "away_score": int(rng.integers(0, 4)),
            "neutral": True, "tournament": "FIFA World Cup",
        })
    wc_df = pd.DataFrame(rows)
    wc_df["played"] = True
    wc_df["year"] = wc_df["date"].dt.year
    wc_df["result"] = np.where(wc_df.home_score > wc_df.away_score, "H",
                               np.where(wc_df.home_score < wc_df.away_score, "A", "D"))
    return pd.concat([df, wc_df], ignore_index=True)


# --------------------------------------------------------------------------- #
# Outcome distribution
# --------------------------------------------------------------------------- #
def test_predict_proba_is_valid_distribution():
    df, teams, _, _ = _history()
    model = models.DixonColesModel().fit(df)
    fixtures = pd.DataFrame({"home_team": teams, "away_team": teams[::-1],
                             "neutral": [True] * len(teams)})
    p = model.predict_proba(fixtures)
    assert p.shape == (len(teams), 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert (p >= 0).all() and (p <= 1).all()


def test_stronger_team_is_favoured():
    df, teams, att, dfc = _history()
    model = models.DixonColesModel().fit(df)
    strong = max(teams, key=lambda t: att[t] + dfc[t])
    weak = min(teams, key=lambda t: att[t] + dfc[t])
    ph, _, pa = model.outcome_probs(strong, weak, neutral=True)
    assert ph > pa  # the stronger side wins more often than it loses


def test_fitted_rho_within_bounds():
    model = models.DixonColesModel().fit(_history()[0])
    lo, hi = model.rho_bounds
    assert lo <= model.rho <= hi


# --------------------------------------------------------------------------- #
# Dixon-Coles low-score correction
# --------------------------------------------------------------------------- #
def test_rho_correction_changes_low_scores_only():
    m = models.DixonColesModel()
    m.base_, m.home_adv_ = 0.2, 0.3
    m.attack_, m.defence_ = {"X": 0.0}, {"X": 0.0}
    m.rho = 0.0
    indep = m.score_matrix("X", "X", neutral=True)
    m.rho = -0.1
    corrected = m.score_matrix("X", "X", neutral=True)
    # The four low-score cells move; both matrices remain valid distributions.
    assert not np.isclose(indep[0, 0], corrected[0, 0])
    assert not np.isclose(indep[1, 1], corrected[1, 1])
    assert np.isclose(indep[3, 4], corrected[3, 4])  # a high score is untouched (pre-renorm)
    assert corrected.sum() == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Cold start / graceful degradation
# --------------------------------------------------------------------------- #
def test_unknown_team_degrades_gracefully():
    model = models.DixonColesModel().fit(_history()[0])
    # A team never seen in training falls back to the league-average prior.
    probs = model.outcome_probs("Atlantis", "T0", neutral=True)
    assert all(np.isfinite(probs))
    assert sum(probs) == pytest.approx(1.0)
    assert model.attack_.get("Atlantis", 0.0) == 0.0  # truly unseen -> prior


def test_sparse_team_is_shrunk_toward_average():
    # A debutant with a single lopsided match must not blow up — ridge pulls it toward 0.
    df, _, _, _ = _history()
    debut = pd.DataFrame([{
        "date": pd.Timestamp("2016-01-01"), "home_team": "Debut", "away_team": "T0",
        "home_score": 9, "away_score": 0, "neutral": False, "tournament": "Friendly",
        "played": True, "year": 2016, "result": "H",
    }])
    model = models.DixonColesModel().fit(pd.concat([df, debut], ignore_index=True))
    # Far less extreme than the 9-0 scoreline would imply unshrunk.
    assert abs(model.attack_["Debut"]) < 1.0
    assert np.isfinite(model.outcome_probs("Debut", "T1")).all()


# --------------------------------------------------------------------------- #
# Simulator interface + as-of fitting
# --------------------------------------------------------------------------- #
def test_sample_scoreline_returns_nonneg_int_pair():
    model = models.DixonColesModel().fit(_history()[0])
    rng = np.random.default_rng(0)
    h, a = model.sample_scoreline("T0", "T1", neutral=True, rng=rng)
    assert isinstance(h, int) and isinstance(a, int)
    assert h >= 0 and a >= 0


def test_sample_scoreline_runs_in_simulator():
    # The whole point: drop the DC model into the real 2026-format simulator unchanged.
    # That simulator needs the 12 groups A-L (48 teams), so fit on a 48-team history.
    rng = np.random.default_rng(1)
    teams = [f"N{i}" for i in range(48)]
    att = {t: float(rng.normal(0, 0.4)) for t in teams}
    dfc = {t: float(rng.normal(0, 0.3)) for t in teams}
    rows, date = [], pd.Timestamp("2014-01-01")
    for _ in range(1600):
        date += pd.Timedelta(days=1)
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({"date": date, "home_team": h, "away_team": a,
                     "home_score": int(rng.poisson(np.exp(0.2 + att[h] - dfc[a]))),
                     "away_score": int(rng.poisson(np.exp(0.2 + att[a] - dfc[h]))),
                     "neutral": True, "tournament": "Friendly"})
    df = pd.DataFrame(rows); df["played"] = True
    model = models.DixonColesModel().fit(df)
    groups = pd.DataFrame({"group": [chr(ord("A") + i // 4) for i in range(48)], "team": teams})
    # No ratings dict: the simulator now reads model.team_strength (DC attack+defence).
    odds = tournament.simulate_tournament(groups, model, n_sims=40, seed=1)
    assert len(odds) == 48
    assert (odds["advance"] <= 1.0).all()
    assert odds["Winner"].sum() == pytest.approx(1.0, abs=0.02)   # exactly one champion per sim
    assert odds["advance"].sum() == pytest.approx(32.0, abs=1e-9)


def test_walk_forward_dixon_coles_runs():
    rows = models.walk_forward_dixon_coles(_wc_frame(), years=(2010,))
    assert len(rows) == 1
    r = rows[0]
    assert r["year"] == 2010 and r["n"] == 8
    assert 0.0 <= r["rps"] <= 1.0


def test_fit_is_as_of_does_not_see_test_only_teams():
    # 'Ghost' appears only in the 2010 WC test fold; fitting on the pre-2010 train must not
    # learn it (proves fit consumes training rows only — as-of, no leakage).
    from wcpred import datasets
    frame = _wc_frame()
    ghost_row = frame.iloc[[0]].copy()
    ghost_row["date"] = pd.Timestamp("2010-06-20")
    ghost_row["home_team"] = "Ghost"
    ghost_row["tournament"] = "FIFA World Cup"
    ghost_row["year"] = 2010
    frame = pd.concat([frame, ghost_row], ignore_index=True)

    train, test = datasets.tournament_holdout(frame, 2010)
    model = models.DixonColesModel().fit(train)
    assert "Ghost" in set(test["home_team"]) | set(test["away_team"])
    assert "Ghost" not in model.attack_
