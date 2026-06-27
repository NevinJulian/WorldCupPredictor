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


# --------------------------------------------------------------------------- #
# Mean-preserving over-dispersion (Step 4 lever)
# --------------------------------------------------------------------------- #
def test_overdispersion_zero_is_poisson():
    """The default (overdispersion=0) is byte-identical to the Poisson pmf — backward-compatible."""
    m = models.DixonColesModel()
    m.base_, m.home_adv_ = 0.3, 0.25
    m.attack_, m.defence_ = {"X": 0.2, "Y": -0.1}, {"X": 0.1, "Y": -0.2}
    m.rho = -0.05
    assert m.overdispersion == 0.0
    assert np.allclose(m._count_pmf(1.7), m._pois_pmf(1.7))
    base = m.score_matrix("X", "Y", neutral=False)
    m2 = models.DixonColesModel(overdispersion=0.0)
    m2.base_, m2.home_adv_, m2.attack_, m2.defence_, m2.rho = m.base_, m.home_adv_, m.attack_, m.defence_, m.rho
    assert np.allclose(base, m2.score_matrix("X", "Y", neutral=False))


def test_overdispersion_preserves_mean_increases_variance():
    """A>0 keeps the marginal mean (mean-preserving) but fattens the tail (higher variance)."""
    k = np.arange(11)
    lam = 1.8
    pois = models.DixonColesModel(overdispersion=0.0)._count_pmf(lam)
    nb = models.DixonColesModel(overdispersion=0.2)._count_pmf(lam)
    # raw pmfs (score_matrix renormalises); truncation at max_goals trims a sliver of the tail
    assert pois.sum() == pytest.approx(1.0, abs=1e-3)
    assert nb.sum() == pytest.approx(1.0, abs=2e-3)
    # same mean (mean-preserving), strictly larger variance
    assert float(k @ nb) == pytest.approx(float(k @ pois), abs=2e-2)
    var_p = float((k * k) @ pois) - (k @ pois) ** 2
    var_n = float((k * k) @ nb) - (k @ nb) ** 2
    assert var_n > var_p + 0.1


def test_overdispersion_keeps_matrix_a_valid_distribution():
    df, teams, _, _ = _history()
    model = models.DixonColesModel(overdispersion=0.15).fit(df)
    M = model.score_matrix(teams[0], teams[1], neutral=True)
    assert M.sum() == pytest.approx(1.0)
    assert (M >= 0).all()


# --------------------------------------------------------------------------- #
# Competition weight (down-weight friendlies) — off by default
# --------------------------------------------------------------------------- #
def _params(m) -> np.ndarray:
    """Flatten a fitted DC model's parameters for an exact comparison."""
    ts = sorted(m.attack_)
    return np.array([m.attack_[t] for t in ts] + [m.defence_[t] for t in ts]
                    + [m.base_, m.home_adv_, m.rho])


def _comp_frame(seed: int = 0):
    """A history where EVERY team plays both competitive and friendly matches (so the team set is
    identical with or without friendlies) — lets `friendly weight 0` be compared to a fit on the
    competitive rows only."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(6)]
    att = {t: float(rng.normal(0, 0.4)) for t in teams}
    dfc = {t: float(rng.normal(0, 0.3)) for t in teams}
    base, adv = 0.2, 0.25
    rows, date = [], pd.Timestamp("2014-01-01")
    for i in range(360):
        date += pd.Timedelta(days=2)
        h, a = rng.choice(teams, 2, replace=False)
        neutral = bool(rng.integers(0, 2))
        lam = np.exp(base + (0.0 if neutral else adv) + att[h] - dfc[a])
        mu = np.exp(base + att[a] - dfc[h])
        # Alternate tiers so every team gets both; competitive label maps to K_QUALIFIER.
        tourn = "FIFA World Cup qualification" if i % 2 == 0 else "Friendly"
        rows.append({"date": date, "home_team": h, "away_team": a,
                     "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
                     "neutral": neutral, "tournament": tourn})
    df = pd.DataFrame(rows)
    df["played"] = True
    df["year"] = df["date"].dt.year
    df["result"] = np.where(df.home_score > df.away_score, "H",
                            np.where(df.home_score < df.away_score, "A", "D"))
    return df


def test_comp_weights_default_is_recency_only():
    """None (default) is byte-identical to an explicit all-ones weighting — backward-compatible,
    off until proven. A {"friendly": 1.0} that names only one tier is also a no-op."""
    df = _comp_frame()
    base = models.DixonColesModel().fit(df)
    all_ones = models.DixonColesModel(
        comp_weights={"competitive": 1.0, "friendly": 1.0, "other": 1.0}).fit(df)
    friendly_one = models.DixonColesModel(comp_weights={"friendly": 1.0}).fit(df)
    assert np.allclose(_params(base), _params(all_ones), atol=1e-9)
    assert np.allclose(_params(base), _params(friendly_one), atol=1e-9)


def test_comp_weights_down_weight_changes_the_fit():
    """A friendly weight below 1 actually moves the fit (the lever does something)."""
    df = _comp_frame()
    base = models.DixonColesModel().fit(df)
    leaned = models.DixonColesModel(comp_weights={"friendly": 0.3}).fit(df)
    assert not np.allclose(_params(base), _params(leaned), atol=1e-3)


def test_comp_weights_zero_friendly_equals_competitive_only():
    """Friendly weight 0 reproduces a fit on the competitive rows alone (same teams, same recency
    reference) — proof the weight keys purely on the tournament tier and removes friendlies'
    influence, with no leakage from the dropped rows' results."""
    from wcpred import datasets
    df = _comp_frame(seed=2)
    ref = df["date"].max()                       # pin the recency reference so both fits match
    comp_only = df[datasets.competition_class(df) == "competitive"].copy()
    assert set(comp_only["home_team"]) | set(comp_only["away_team"]) == set(df["home_team"]) | set(df["away_team"])
    zeroed = models.DixonColesModel(comp_weights={"friendly": 0.0}).fit(df, ref_date=ref)
    dropped = models.DixonColesModel().fit(comp_only, ref_date=ref)
    assert np.allclose(_params(zeroed), _params(dropped), atol=1e-6)


def test_comp_weights_is_as_of_does_not_see_test_only_teams():
    """The competition weight does not break as-of fitting: a test-only team is still never learned
    (the weight depends on tournament label + date, never the outcome or future rows)."""
    from wcpred import datasets
    frame = _wc_frame()
    ghost = frame.iloc[[0]].copy()
    ghost["date"] = pd.Timestamp("2010-06-20")
    ghost["home_team"] = "Ghost"
    ghost["tournament"] = "FIFA World Cup"
    ghost["year"] = 2010
    frame = pd.concat([frame, ghost], ignore_index=True)
    train, test = datasets.tournament_holdout(frame, 2010)
    model = models.DixonColesModel(comp_weights={"friendly": 0.4}).fit(train)
    assert "Ghost" in set(test["home_team"]) | set(test["away_team"])
    assert "Ghost" not in model.attack_


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
