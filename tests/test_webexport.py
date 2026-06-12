"""Unit tests for the web-export layer (wcpred.webexport). Synthetic + committed artifacts.

Two kinds of check:
  * SYNTHETIC (CI-safe, no real data): the export helpers preserve the model's accounting —
    game-mode distributions read the matrix correctly, the tournament section sums to one champion
    / 32 qualifiers per sim with monotone reach odds and full per-group placement, the chalk
    bracket is the deterministic 31-tie path, and the Annex-C structure is the real 495-combo table.
  * ARTIFACT CROSS-CHECK (CI-safe, reads committed JSON): the exported group-stage fixtures match
    the frozen data/processed/forecast_2026.json field-for-field — the export reflects the shipped
    model. Skipped only if web/data/model_export.json has not been generated yet.
Run: `pytest -q`
"""
import json
import pathlib
import sys
from itertools import combinations

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import forecast, webexport  # noqa: E402


# --------------------------------------------------------------------------- #
# Synthetic fixtures
# --------------------------------------------------------------------------- #
def _synth48(seed: int = 0):
    """A 48-team synthetic ForecastMatchModel (all neutral pairs), groups A-L, fixtures-by-group."""
    teams = [f"T{i}" for i in range(48)]
    idx = {t: i for i, t in enumerate(teams)}
    base = np.ones((6, 6)) / 36.0
    mats = {}
    for a in teams:
        for b in teams:
            if a == b:
                continue
            pa = 1.0 / (1.0 + 10 ** (-(idx[a] - idx[b]) * 0.05))   # higher index favoured
            pd_ = 0.24
            mats[(a, b)] = forecast.reweight_to_outcome(base, ((1 - pd_) * pa, pd_, (1 - pd_) * (1 - pa)))
    model = forecast.ForecastMatchModel(mats, {t: 1500.0 + idx[t] * 7 for t in teams})
    gt = {chr(ord("A") + i): teams[i * 4:i * 4 + 4] for i in range(12)}
    team_group = {t: g for g, ts in gt.items() for t in ts}
    fbg = {g: list(combinations(ts, 2)) for g, ts in gt.items()}
    return model, gt, team_group, fbg, mats


def _ident(t):
    return t


# --------------------------------------------------------------------------- #
# Game mode
# --------------------------------------------------------------------------- #
def test_game_mode_records_read_the_matrix():
    teams = ["Alpha", "Bravo", "Charlie", "Delta"]
    mats = {}
    rng = np.random.default_rng(1)
    for a in teams:
        for b in teams:
            if a != b:
                tgt = rng.dirichlet([3, 2, 3])
                # A non-uniform base so each outcome region has a unique cell maximum (real DC
                # matrices do too); a uniform base would tie every draw cell and make "the modal
                # scoreline" ill-defined.
                base = rng.random((6, 6)) + 0.05
                base /= base.sum()
                mats[(a, b)] = forecast.reweight_to_outcome(base, tuple(tgt))
    recs = webexport.game_mode_records(mats, teams, _ident)
    assert len(recs) == 6                                   # C(4,2) unordered pairs
    for r in recs:
        assert r["home"] < r["away"]                        # display-name ordered, unordered pair
        probs = [p for _, p in r["top"]]
        assert probs == sorted(probs, reverse=True)         # top-3 descending
        assert r["p_home"] + r["p_draw"] + r["p_away"] == pytest.approx(1.0, abs=2e-4)
        # modal scoreline is the argmax of the matrix it was read from
        M = mats[(r["home"], r["away"])]
        x, y = np.unravel_index(int(M.argmax()), M.shape)
        assert r["modal"] == f"{x}-{y}"


def test_game_mode_is_neutral_not_host_aware():
    """The same pair scored from a neutral vs a host-tilted matrix must differ — game mode uses
    the neutral one. Guards that we export `info['neutral_matrices']`, not the host overrides."""
    neutral = forecast.reweight_to_outcome(np.ones((6, 6)) / 36.0, (0.40, 0.30, 0.30))
    host = forecast.reweight_to_outcome(np.ones((6, 6)) / 36.0, (0.65, 0.20, 0.15))
    rec = webexport.game_mode_records({("A", "B"): neutral, ("B", "A"): neutral.T}, ["A", "B"], _ident)[0]
    assert rec["p_home"] == pytest.approx(0.40, abs=2e-4)   # neutral marginals, not the host 0.65


# --------------------------------------------------------------------------- #
# Tournament
# --------------------------------------------------------------------------- #
def test_tournament_records_accounting_and_placement():
    model, gt, team_group, _, _ = _synth48()
    by_n = webexport.tournament_records(model, gt, team_group, _ident, levels=(200,), seed=3)
    sec = by_n["200"]
    teams = sec["teams"]
    assert len(teams) == 48
    # one champion and 32 qualifiers per sim (within 4dp rounding over 48 teams)
    assert sum(t["title"] for t in teams) == pytest.approx(1.0, abs=0.01)
    assert sum(t["advance"] for t in teams) == pytest.approx(32.0, abs=0.05)
    # reach odds are nested per team
    for t in teams:
        assert t["advance"] >= t["R16"] >= t["QF"] >= t["SF"] >= t["Final"] >= t["title"]
    # per-group placement: 12 groups of 4, advance-descending, win+runner_up+third <= 1
    assert set(sec["groups"]) == set("ABCDEFGHIJKL")
    for g, recs in sec["groups"].items():
        assert len(recs) == 4
        advs = [r["advance"] for r in recs]
        assert advs == sorted(advs, reverse=True)
        for r in recs:
            assert 0.0 <= r["win"] + r["runner_up"] + r["third"] <= 1.0 + 1e-9


def test_tournament_levels_all_present():
    model, gt, team_group, _, _ = _synth48()
    by_n = webexport.tournament_records(model, gt, team_group, _ident, levels=(100, 200), seed=1)
    assert set(by_n) == {"100", "200"}


# --------------------------------------------------------------------------- #
# Chalk bracket
# --------------------------------------------------------------------------- #
def test_chalk_records_structure():
    model, gt, team_group, fbg, _ = _synth48()
    ch = webexport.chalk_records(model, gt, fbg, _ident)
    counts = {r: sum(1 for t in ch["bracket"] if t["round"] == r)
              for r in ("R32", "R16", "QF", "SF", "Final")}
    assert counts == {"R32": 16, "R16": 8, "QF": 4, "SF": 2, "Final": 1}
    assert len(ch["best_thirds"]) == 8
    for t in ch["bracket"]:
        assert t["winner"] in (t["home"], t["away"])
        assert "-" in t["modal"]


# --------------------------------------------------------------------------- #
# Structure / Annex-C
# --------------------------------------------------------------------------- #
def test_structure_records_annexc_is_real_table():
    teams = [f"T{i}" for i in range(48)]
    gt = {chr(ord("A") + i): teams[i * 4:i * 4 + 4] for i in range(12)}
    st = webexport.structure_records(gt, teams, _ident)
    assert set(st["groups"]) == set("ABCDEFGHIJKL")
    assert all(len(v) == 4 for v in st["groups"].values())
    assert st["annexc"]["n_combinations"] == 495                 # the real Annex-C table
    assert len(st["annexc"]["third_facing_winners"]) == 8
    assert len(st["annexc"]["r32_bracket"]) == 16
    assert len(st["confederations"]) == 48


# --------------------------------------------------------------------------- #
# Artifact cross-check — exported group fixtures match the frozen forecast record
# --------------------------------------------------------------------------- #
_EXPORT = ROOT / "web" / "data" / "model_export.json"
_FROZEN = ROOT / "data" / "processed" / "forecast_2026.json"


@pytest.mark.skipif(not _EXPORT.exists(), reason="web/data/model_export.json not generated yet")
def test_group_fixtures_match_frozen_forecast():
    export = json.loads(_EXPORT.read_text(encoding="utf-8"))
    frozen = json.loads(_FROZEN.read_text(encoding="utf-8"))
    exp = {(r["home"], r["away"]): r for r in export["group_stage"]}
    assert len(frozen["fixtures"]) == len(exp) == 72
    for fx in frozen["fixtures"]:
        r = exp[(fx["home"], fx["away"])]
        assert r["group"] == fx["group"]
        assert r["modal"] == fx["most_likely"]                  # modal == most-likely scoreline
        assert r["e_home"] == pytest.approx(fx["e_home"], abs=1e-3)
        assert r["e_away"] == pytest.approx(fx["e_away"], abs=1e-3)
        assert r["p_home"] == pytest.approx(fx["p_home"], abs=1e-4)
        assert r["p_draw"] == pytest.approx(fx["p_draw"], abs=1e-4)
        assert r["p_away"] == pytest.approx(fx["p_away"], abs=1e-4)


@pytest.mark.skipif(not _EXPORT.exists(), reason="web/data/model_export.json not generated yet")
def test_export_shape_and_metadata():
    export = json.loads(_EXPORT.read_text(encoding="utf-8"))
    assert export["metadata"]["model_version"] == "0.4.0"
    assert export["metadata"]["confed_calibration"] is True
    assert len(export["game_mode"]) == 48 * 47 // 2            # C(48,2) unordered pairs
    assert set(export["tournament"]["by_n"]) == {"1000", "10000", "50000", "100000"}
    # title sums to ~1 champion at the largest N
    teams = export["tournament"]["by_n"]["100000"]["teams"]
    assert sum(t["title"] for t in teams) == pytest.approx(1.0, abs=0.01)
