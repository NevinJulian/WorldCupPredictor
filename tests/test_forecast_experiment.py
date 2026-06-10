"""Unit tests for the frozen-forecast reporting helpers (wcpred.forecast). No network.

Guards: the Monte-Carlo accounting is exact (one champion and 32 qualifiers per sim, every team
placed once), the no-sim expected-goals reads the matrix marginals correctly, and the traced
scenario is a complete, internally-consistent single realization. Run: `pytest -q`
"""
import pathlib
import sys
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import forecast, tournament  # noqa: E402


def _elo_setup(seed: int = 0):
    teams = [f"T{i}" for i in range(48)]
    groups = pd.DataFrame({"group": [chr(ord("A") + i // 4) for i in range(48)], "team": teams})
    rng = np.random.default_rng(seed)
    model = tournament.EloMatchModel({t: 1500 + float(rng.normal(0, 120)) for t in teams})
    return model, forecast.groups_by_name(groups)


# --------------------------------------------------------------------------- #
# Probabilities — exact accounting
# --------------------------------------------------------------------------- #
def test_run_probabilities_accounting_is_exact():
    model, gt = _elo_setup()
    N = 400
    reach, place = forecast.run_probabilities(model, gt, N, seed=1)
    assert len(reach) == 48 and len(place) == 48
    # exactly one champion and 32 qualifiers per simulation
    assert sum(r["title"] for r in reach.values()) == N
    assert sum(r["advance"] for r in reach.values()) == 32 * N
    # every team finishes somewhere each sim; 12 group winners per sim
    assert all(sum(place[t]) == N for t in place)
    assert sum(p[0] for p in place.values()) == 12 * N
    # nested rounds: advance >= R16 >= QF >= SF >= Final >= title per team
    for t, r in reach.items():
        assert r["advance"] >= r["R16"] >= r["QF"] >= r["SF"] >= r["Final"] >= r["title"]


def test_run_probabilities_matches_simulate_tournament():
    # Same model + seed: the reused shipped internals give the same aggregates.
    model, gt = _elo_setup()
    groups = pd.DataFrame({"group": [g for g, ts in gt.items() for _ in ts],
                           "team": [t for ts in gt.values() for t in ts]})
    reach, _ = forecast.run_probabilities(model, gt, 300, seed=7)
    odds = tournament.simulate_tournament(groups, model, n_sims=300, seed=7).set_index("team")
    # simulate_tournament rounds each team to 4dp, so compare within that rounding tolerance.
    assert sum(r["advance"] for r in reach.values()) / 300 == pytest.approx(odds["advance"].sum(), abs=1e-2)
    assert sum(r["title"] for r in reach.values()) / 300 == pytest.approx(odds["Winner"].sum(), abs=1e-2)
    # per-team title agrees to the rounding (same seed + same shipped internals -> same counts)
    for t, r in reach.items():
        assert r["title"] / 300 == pytest.approx(float(odds.loc[t, "Winner"]), abs=1e-3)


# --------------------------------------------------------------------------- #
# Expected goals — no simulation, reads the scoreline matrix
# --------------------------------------------------------------------------- #
def test_fixture_goal_model_reads_matrix_marginals():
    M = forecast.reweight_to_outcome(np.ones((6, 6)) / 36.0, (0.55, 0.25, 0.20))
    model = forecast.ForecastMatchModel({("X", "Y"): M}, {})
    fg = forecast.fixture_goal_model(model, "X", "Y")
    assert fg["p_home"] == pytest.approx(0.55)
    assert fg["p_draw"] == pytest.approx(0.25)
    assert fg["p_away"] == pytest.approx(0.20)
    assert fg["e_home"] >= 0 and fg["e_away"] >= 0
    assert isinstance(fg["most_likely"], tuple) and len(fg["most_likely"]) == 2


# --------------------------------------------------------------------------- #
# One sampled scenario — complete, internally consistent
# --------------------------------------------------------------------------- #
def test_simulate_traced_is_a_complete_realization():
    model, gt = _elo_setup()
    sc = forecast.simulate_traced(model, gt, seed=3)
    all_teams = {t for ts in gt.values() for t in ts}
    assert sc["champion"] in all_teams
    assert len(sc["best_thirds"]) == 8
    # bracket: 16 + 8 + 4 + 2 + 1 = 31 ties
    counts = {r: sum(1 for t in sc["bracket"] if t[0] == r) for r in ("R32", "R16", "QF", "SF", "Final")}
    assert counts == {"R32": 16, "R16": 8, "QF": 4, "SF": 2, "Final": 1}
    # the Final's winner is the champion
    final = [t for t in sc["bracket"] if t[0] == "Final"][0]
    assert final[5] == sc["champion"]
    # each group has 4 ranked teams and its 6 round-robin scorelines
    for g, d in sc["groups"].items():
        assert len(d["table"]) == 4 and len(d["fixtures"]) == 6
    # every knockout winner is one of the two teams in its tie
    for _, a, b, _, _, w, _ in sc["bracket"]:
        assert w in (a, b)


# --------------------------------------------------------------------------- #
# Scoreline distributions + deterministic chalk bracket
# --------------------------------------------------------------------------- #
def test_top_scorelines_descending_and_modal_is_argmax():
    M = np.array([[0.30, 0.10, 0.02], [0.20, 0.15, 0.03], [0.10, 0.05, 0.05]])
    M = M / M.sum()
    model = forecast.ForecastMatchModel({("X", "Y"): M}, {})
    d = forecast.fixture_scoreline_distribution(model, "X", "Y", top_k=3)
    probs = [p for _, p in d["top"]]
    assert probs == sorted(probs, reverse=True)              # top-3 probabilities descending
    assert d["modal"] == (0, 0)                              # matrix argmax
    assert d["top"][0][0] == d["modal"]


def test_modal_bucket_matches_matrix_argmax():
    M = np.array([[0.30, 0.10, 0.02], [0.20, 0.15, 0.03], [0.10, 0.05, 0.05]])
    M = M / M.sum()
    model = forecast.ForecastMatchModel({("X", "Y"): M}, {})
    rng = np.random.default_rng(0)
    counts = Counter(model.sample_scoreline("X", "Y", rng=rng) for _ in range(20000))
    modal_bucket = counts.most_common(1)[0][0]
    assert modal_bucket == forecast.fixture_scoreline_distribution(model, "X", "Y")["modal"]


def _synthetic_chalk_model():
    teams = [f"T{i}" for i in range(48)]
    idx = {t: i for i, t in enumerate(teams)}
    base = np.ones((4, 4)) / 16.0
    mats = {}
    for a in teams:
        for b in teams:
            if a == b:
                continue
            pa = 1.0 / (1.0 + 10 ** (-(idx[a] - idx[b]) * 0.06))   # stronger (higher idx) favoured
            pd_ = 0.22
            mats[(a, b)] = forecast.reweight_to_outcome(base, (pd_ * 0 + (1 - pd_) * pa, pd_, (1 - pd_) * (1 - pa)))
    model = forecast.ForecastMatchModel(mats, {t: 1500.0 + idx[t] * 8 for t in teams})
    groups = {chr(ord("A") + i): teams[i * 4:i * 4 + 4] for i in range(12)}
    fbg = {g: list(combinations(ts, 2)) for g, ts in groups.items()}
    return model, groups, fbg, idx


def test_chalk_bracket_is_deterministic_and_favourites_advance():
    model, groups, fbg, idx = _synthetic_chalk_model()
    ch = forecast.chalk_bracket(model, groups, fbg)
    # deterministic: a second call is identical
    assert forecast.chalk_bracket(model, groups, fbg)["bracket"] == ch["bracket"]
    assert len(ch["best_thirds"]) == 8
    counts = {r: sum(1 for t in ch["bracket"] if t[0] == r) for r in ("R32", "R16", "QF", "SF", "Final")}
    assert counts == {"R32": 16, "R16": 8, "QF": 4, "SF": 2, "Final": 1}
    # in every tie the higher-strength (= higher win-prob) team advances
    for _, a, b, _, w, pa, pb in ch["bracket"]:
        assert idx[w] == max(idx[a], idx[b])
        assert (w == a) == (pa >= pb)
    # the strongest team holds chalk all the way to the title
    assert ch["champion"] == "T47"
