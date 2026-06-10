"""Unit tests for the 2026 forecast layer (wcpred.forecast). Synthetic, no network.

Load-bearing checks: (1) the outcome reweighting makes a DC score matrix's H/D/A marginals
equal the ensemble target exactly; (2) the per-team snapshot is leakage-free — a team's
snapshot form is the mean over its last played matches, with no contamination from the
synthetic fixtures; (3) build_forecast_model assembles a model that drops into the simulator.
Run: `pytest -q`
"""
import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import forecast, models, tournament  # noqa: E402


def _clean_frame(teams, n=600, seed=0) -> pd.DataFrame:
    """A clean.load_clean_results-shaped frame: played friendlies among `teams`."""
    rng = np.random.default_rng(seed)
    skill = {t: float(rng.uniform(0.7, 2.6)) for t in teams}
    rows, date = [], pd.Timestamp("2012-01-01")
    for _ in range(n):
        date += pd.Timedelta(days=3)
        h, a = rng.choice(teams, 2, replace=False)
        hs, as_ = int(rng.poisson(skill[h])), int(rng.poisson(skill[a]))
        rows.append({"date": date, "home_team": h, "away_team": a, "home_score": hs,
                     "away_score": as_, "tournament": "Friendly", "neutral": bool(rng.integers(0, 2))})
    m = pd.DataFrame(rows)
    m["played"] = True
    m["margin"] = m["home_score"] - m["away_score"]
    m["total_goals"] = m["home_score"] + m["away_score"]
    m["result"] = np.where(m.margin > 0, "H", np.where(m.margin < 0, "A", "D"))
    m["year"] = m["date"].dt.year
    return m


# --------------------------------------------------------------------------- #
# Outcome reweighting
# --------------------------------------------------------------------------- #
def test_reweight_matches_target_marginals_exactly():
    rng = np.random.default_rng(1)
    P = rng.random((6, 6)) + 0.01
    P /= P.sum()
    target = (0.6, 0.25, 0.15)
    R = forecast.reweight_to_outcome(P, target)
    pH = np.tril(R, -1).sum()
    pD = np.trace(R)
    pA = np.triu(R, 1).sum()
    assert R.sum() == pytest.approx(1.0)
    assert (pH, pD, pA) == pytest.approx(target)
    assert (R >= 0).all()


def test_reweight_preserves_conditional_shape_within_outcome():
    # Within the home-win cells the relative proportions are unchanged (uniform scaling).
    rng = np.random.default_rng(2)
    P = rng.random((5, 5)) + 0.01
    P /= P.sum()
    R = forecast.reweight_to_outcome(P, (0.5, 0.2, 0.3))
    tl = np.tril(np.ones((5, 5)), -1).astype(bool)
    ratio = (R[tl] / P[tl])
    assert np.allclose(ratio, ratio[0])   # one common factor across all home-win cells


# --------------------------------------------------------------------------- #
# Arithmetic assembly
# --------------------------------------------------------------------------- #
def test_assemble_pairs_columns_and_diffs():
    snap = {
        "X": {"elo": 1800.0, "rank": 5.0, "rank_points": 1700.0, "confed": "UEFA",
              **{b: 1.0 for b in forecast._BASE_FORM}},
        "Y": {"elo": 1600.0, "rank": 20.0, "rank_points": 1400.0, "confed": "CAF",
              **{b: 0.4 for b in forecast._BASE_FORM}},
    }
    df = forecast.assemble_pairs(snap, [("X", "Y")])
    r = df.iloc[0]
    assert {"home_team", "away_team", "neutral"} <= set(df.columns)
    assert r["elo_diff"] == pytest.approx(200.0)
    assert r["rank_diff"] == pytest.approx(-15.0)
    assert r["same_confed"] == 0                                  # UEFA != CAF
    assert r["form_ppg_5_diff"] == pytest.approx(0.6)
    assert r["elo_expected_home"] == pytest.approx(1 / (1 + 10 ** (-200 / 400)))


# --------------------------------------------------------------------------- #
# Snapshot is leakage-free (no contamination)
# --------------------------------------------------------------------------- #
def test_team_snapshot_form_is_as_of_played_history():
    teams = [f"T{i}" for i in range(8)]
    m = _clean_frame(teams, n=500, seed=3)
    snap = forecast.team_snapshot(m, ranking=None, teams=teams, hosts=set())
    assert set(snap) == set(teams)

    # Recompute one team's last-5 points-per-game by hand; the snapshot must match it
    # (proves the form is over the team's played history, uncontaminated by the synth row).
    t = "T0"
    sub = m[(m["home_team"] == t) | (m["away_team"] == t)].sort_values("date")
    pts = []
    for _, row in sub.iterrows():
        gf, ga = (row["home_score"], row["away_score"]) if row["home_team"] == t else (row["away_score"], row["home_score"])
        pts.append(3.0 if gf > ga else (1.0 if gf == ga else 0.0))
    expected_ppg5 = float(np.mean(pts[-5:]))
    assert snap[t]["form_ppg_5"] == pytest.approx(expected_ppg5)


def test_team_snapshot_requires_even_team_count():
    m = _clean_frame([f"T{i}" for i in range(4)], n=120, seed=4)
    with pytest.raises(ValueError):
        forecast.team_snapshot(m, ranking=None, teams=[f"T{i}" for i in range(3)], hosts=set())


# --------------------------------------------------------------------------- #
# ForecastMatchModel
# --------------------------------------------------------------------------- #
def test_forecast_model_sampling_honours_reweighted_marginals():
    P = forecast.reweight_to_outcome(np.ones((4, 4)) / 16.0, (0.5, 0.2, 0.3))
    model = forecast.ForecastMatchModel({("X", "Y"): P}, {"X": 1.0, "Y": 0.0})
    assert model.team_strength("X") > model.team_strength("Y")
    rng = np.random.default_rng(0)
    h = d = a = 0
    n = 6000
    for _ in range(n):
        gh, ga = model.sample_scoreline("X", "Y", neutral=True, rng=rng)
        h, d, a = (h + (gh > ga), d + (gh == ga), a + (gh < ga))
    assert h / n == pytest.approx(0.5, abs=0.03)
    assert d / n == pytest.approx(0.2, abs=0.03)
    assert a / n == pytest.approx(0.3, abs=0.03)


def test_forecast_model_unknown_pair_falls_back():
    model = forecast.ForecastMatchModel({}, {})
    gh, ga = model.sample_scoreline("U", "V", neutral=True, rng=np.random.default_rng(0))
    assert gh >= 0 and ga >= 0


# --------------------------------------------------------------------------- #
# Strength-uncertainty dispersion lever (rating_sigma)
# --------------------------------------------------------------------------- #
def _hda(X):
    return float(np.tril(X, -1).sum()), float(np.trace(X)), float(np.triu(X, 1).sum())


def test_tilt_shifts_winshare_and_preserves_draw():
    fm = forecast.ForecastMatchModel({}, {})
    M = forecast.reweight_to_outcome(np.ones((4, 4)) / 16.0, (0.4, 0.3, 0.3))
    pH0, pD0, pA0 = _hda(M)
    up = fm._tilt(M, 0.6)                       # positive supremacy favours home
    pH1, pD1, pA1 = _hda(up)
    assert pH1 > pH0 and pA1 < pA0
    assert pD1 == pytest.approx(pD0)            # draw mass preserved
    assert up.sum() == pytest.approx(1.0)
    assert _hda(fm._tilt(M, -0.6))[0] < pH0     # negative favours away
    assert np.allclose(fm._tilt(M, 0.0), M)     # zero delta is a no-op


def test_begin_tournament_shock_behaviour():
    fm = forecast.ForecastMatchModel({}, {"A": 1800.0, "B": 1500.0}, rating_sigma=0.0)
    fm.begin_tournament(np.random.default_rng(0))
    assert fm._shock is None                    # off by default
    fm.rating_sigma = 80.0
    fm.begin_tournament(np.random.default_rng(0))
    assert set(fm._shock) == {"A", "B"}
    assert all(isinstance(v, float) for v in fm._shock.values())


def test_rating_sigma_zero_is_passthrough():
    # With the lever off, begin_tournament + sample_scoreline reproduce the matrix marginals.
    P = forecast.reweight_to_outcome(np.ones((4, 4)) / 16.0, (0.5, 0.2, 0.3))
    fm = forecast.ForecastMatchModel({("X", "Y"): P}, {"X": 1.0, "Y": 0.0}, rating_sigma=0.0)
    fm.begin_tournament(np.random.default_rng(0))
    rng = np.random.default_rng(1)
    h = d = a = 0
    n = 6000
    for _ in range(n):
        gh, ga = fm.sample_scoreline("X", "Y", rng=rng)
        h, d, a = (h + (gh > ga), d + (gh == ga), a + (gh < ga))
    assert h / n == pytest.approx(0.5, abs=0.03)
    assert d / n == pytest.approx(0.2, abs=0.03)


def test_simulate_tournament_invokes_begin_tournament_each_sim():
    calls = {"n": 0}

    class Stub:
        strength_scale = 400.0

        def begin_tournament(self, rng):
            calls["n"] += 1

        def team_strength(self, t):
            return 1500.0

        def sample_scoreline(self, a, b, neutral=True, rng=None):
            rng = rng or np.random.default_rng()
            return int(rng.integers(0, 3)), int(rng.integers(0, 3))

    teams = [f"T{i}" for i in range(48)]
    groups = pd.DataFrame({"group": [chr(ord("A") + i // 4) for i in range(48)], "team": teams})
    tournament.simulate_tournament(groups, Stub(), n_sims=3, seed=0)
    assert calls["n"] == 3


# --------------------------------------------------------------------------- #
# End-to-end assembly + simulation
# --------------------------------------------------------------------------- #
def test_build_forecast_model_end_to_end():
    teams = [f"T{i}" for i in range(8)]
    m = _clean_frame(teams, n=700, seed=5)
    groups = pd.DataFrame({"group": ["A"] * 4 + ["B"] * 4, "team": teams,
                           "confederation": ["UEFA"] * 8, "is_pot1": [1, 0, 0, 0, 1, 0, 0, 0]})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model, sim_groups, display, info = forecast.build_forecast_model(
            matches=m, ranking=None, groups=groups, ensemble_kwargs={"gbm_kwargs": {"max_iter": 60}})
    # every ordered tournament pair has a precomputed scoreline matrix
    for a in teams:
        for b in teams:
            if a != b:
                assert (a, b) in model.matrices
    assert 0.0 <= info["ensemble_weight"] <= 1.0
    # The assembled model satisfies the simulator's match-model interface (the real 12-group
    # Annex-C simulation itself is covered in test_tournament.py).
    gh, ga = model.sample_scoreline(teams[0], teams[1], neutral=True, rng=np.random.default_rng(0))
    assert gh >= 0 and ga >= 0
    assert isinstance(model.team_strength(teams[0]), float)
