"""Data-contract guard for the web UI: web/data/model_export.json must keep the shape the
front-end (web/app.js) depends on. This is committed alongside the UI, so it runs in CI even
without the raw data — if the export schema drifts, the site silently breaks and this fails first.
Run: `pytest -q`
"""
import json
import math
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPORT = ROOT / "web" / "data" / "model_export.json"

pytestmark = pytest.mark.skipif(not EXPORT.exists(), reason="web/data/model_export.json missing")


@pytest.fixture(scope="module")
def data():
    return json.loads(EXPORT.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
def test_metadata_has_version_and_as_of(data):
    md = data["metadata"]
    assert md["model_version"] == "0.4.0"
    assert isinstance(md["as_of"], str) and md["as_of"]          # footer shows this
    assert md["confed_calibration"] is True


def test_structure_48_teams_groups_confeds(data):
    st = data["structure"]
    assert set(st["groups"]) == set("ABCDEFGHIJKL")
    teams = [t for ts in st["groups"].values() for t in ts]
    assert len(teams) == 48 and len(set(teams)) == 48           # the dropdown population
    # every team has a confederation (the UI tags it)
    for t in teams:
        assert st["confederations"].get(t), f"no confederation for {t}"
    assert st["annexc"]["n_combinations"] == 495


_DIST_FIELDS = ("modal", "top", "e_home", "e_away", "p_home", "p_draw", "p_away",
                "p_over25", "goal_totals")


def _check_dist(r):
    """Validate the per-fixture distribution fields the detail panel relies on."""
    for f in _DIST_FIELDS:
        assert f in r, f"record missing '{f}'"
    assert "-" in r["modal"]
    # top-6 scorelines, probability-descending, each a 'x-y'
    assert len(r["top"]) == 6
    probs = [p for _, p in r["top"]]
    assert probs == sorted(probs, reverse=True) and all("-" in s for s, _ in r["top"])
    assert math.isclose(r["p_home"] + r["p_draw"] + r["p_away"], 1.0, abs_tol=2e-3)
    # total-goals distribution P(0,1,2,3,4,5+) sums to 1; P(over 2.5) == P(total >= 3)
    gt = r["goal_totals"]
    assert len(gt) == 6 and all(0.0 <= x <= 1.0 for x in gt)
    assert math.isclose(sum(gt), 1.0, abs_tol=2e-3)
    assert 0.0 <= r["p_over25"] <= 1.0
    assert math.isclose(r["p_over25"], gt[3] + gt[4] + gt[5], abs_tol=2e-3)


def test_game_mode_is_all_1128_pairs_with_fields(data):
    gm = data["game_mode"]
    teams = [t for ts in data["structure"]["groups"].values() for t in ts]
    assert len(gm) == len(teams) * (len(teams) - 1) // 2        # C(48,2) = 1128
    seen = set()
    teamset = set(teams)
    for r in gm:
        assert "home" in r and "away" in r
        assert r["home"] in teamset and r["away"] in teamset and r["home"] != r["away"]
        key = frozenset((r["home"], r["away"]))
        assert key not in seen, f"duplicate pair {r['home']}/{r['away']}"
        seen.add(key)
        _check_dist(r)
    assert len(seen) == 1128                                    # every unordered pair, once


def test_every_team_pair_is_resolvable_either_orientation(data):
    """The UI looks up (a,b) then (b,a); confirm one orientation exists for all C(48,2) pairs."""
    teams = sorted(t for ts in data["structure"]["groups"].values() for t in ts)
    keys = {(r["home"], r["away"]) for r in data["game_mode"]}
    for i, a in enumerate(teams):
        for b in teams[i + 1:]:
            assert (a, b) in keys or (b, a) in keys, f"no pair for {a}/{b}"


def test_group_stage_72_fixtures_with_fields(data):
    gs = data["group_stage"]
    assert len(gs) == 72                                        # always all 72, played or not
    for r in gs:
        assert "group" in r and "home" in r and "away" in r
        assert isinstance(r["played"], bool)
        if r["played"]:
            # played fixtures carry the real result ...
            assert isinstance(r["home_score"], int) and isinstance(r["away_score"], int)
            assert r["home_score"] >= 0 and r["away_score"] >= 0
            assert r["result"] in ("H", "D", "A")
            # ... and keep the pre-match prediction for grading (reduced fields from the immutable
            # snapshot; None only if the snapshot predates the fixture).
            pred = r["prediction"]
            if pred is not None:
                assert "-" in pred["modal"]
                assert math.isclose(pred["p_home"] + pred["p_draw"] + pred["p_away"], 1.0, abs_tol=2e-3)
        else:
            _check_dist(r)


def test_tournament_levels_and_reach_fields(data):
    tour = data["tournament"]
    assert set(tour["by_n"]) == {"1000", "10000", "50000", "100000"}
    for n, sec in tour["by_n"].items():
        assert len(sec["teams"]) == 48
        for t in sec["teams"]:
            for f in ("team", "group", "advance", "R16", "QF", "SF", "Final", "title"):
                assert f in t
        assert set(sec["groups"]) == set("ABCDEFGHIJKL")
    # chalk bracket present and complete (31 ties)
    ch = tour["chalk"]
    assert ch["champion"] and len(ch["bracket"]) == 31


# --------------------------------------------------------------------------- #
# Flags — every team resolves to a bundled SVG (the UI shows flags everywhere)
# --------------------------------------------------------------------------- #
_FLAGS_DIR = ROOT / "web" / "flags"
_FLAGS_MAP = _FLAGS_DIR / "flags.json"

# The non-trivial codes the UI must get right (subdivisions / spelling).
_TRICKY = {
    "England": "gb-eng", "Scotland": "gb-sct", "Curaçao": "cw", "Cape Verde": "cv",
    "DR Congo": "cd", "Ivory Coast": "ci", "South Korea": "kr", "United States": "us",
    "Türkiye": "tr", "Uzbekistan": "uz", "Bosnia and Herzegovina": "ba",
}


def test_every_team_has_a_bundled_flag(data):
    assert _FLAGS_MAP.exists(), "web/flags/flags.json missing"
    fmap = json.loads(_FLAGS_MAP.read_text(encoding="utf-8"))
    teams = [t for ts in data["structure"]["groups"].values() for t in ts]
    for t in teams:
        assert t in fmap, f"no flag mapping for team '{t}'"
        iso = fmap[t]
        assert (_FLAGS_DIR / (iso + ".svg")).exists(), f"missing flag SVG for {t} ({iso}.svg)"
    # the tricky ones are mapped exactly as required
    for team, iso in _TRICKY.items():
        assert fmap.get(team) == iso, f"{team} should map to {iso}, got {fmap.get(team)}"
    # a neutral placeholder exists for the fallback path
    assert (_FLAGS_DIR / "_placeholder.svg").exists()


def test_flag_map_has_no_dangling_entries(data):
    """Every flag mapping points at a real SVG and a real team (no rot)."""
    fmap = json.loads(_FLAGS_MAP.read_text(encoding="utf-8"))
    teams = set(t for ts in data["structure"]["groups"].values() for t in ts)
    for team, iso in fmap.items():
        assert team in teams, f"flags.json has unknown team '{team}'"
        assert (_FLAGS_DIR / (iso + ".svg")).exists(), f"flags.json -> missing {iso}.svg"
