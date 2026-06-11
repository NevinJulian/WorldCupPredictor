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
    assert md["model_version"] == "0.2.0"
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


_GAME_FIELDS = ("home", "away", "modal", "top", "e_home", "e_away", "p_home", "p_draw", "p_away")


def test_game_mode_is_all_1128_pairs_with_fields(data):
    gm = data["game_mode"]
    teams = [t for ts in data["structure"]["groups"].values() for t in ts]
    assert len(gm) == len(teams) * (len(teams) - 1) // 2        # C(48,2) = 1128
    seen = set()
    teamset = set(teams)
    for r in gm:
        for f in _GAME_FIELDS:
            assert f in r, f"game_mode record missing '{f}'"
        assert r["home"] in teamset and r["away"] in teamset and r["home"] != r["away"]
        key = frozenset((r["home"], r["away"]))
        assert key not in seen, f"duplicate pair {r['home']}/{r['away']}"
        seen.add(key)
        # modal is a 'x-y' scoreline; top is descending [['x-y', p], ...]
        assert "-" in r["modal"]
        probs = [p for _, p in r["top"]]
        assert probs == sorted(probs, reverse=True) and all("-" in s for s, _ in r["top"])
        assert math.isclose(r["p_home"] + r["p_draw"] + r["p_away"], 1.0, abs_tol=2e-3)
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
    assert len(gs) == 72
    for r in gs:
        for f in ("group", "home", "away", "modal", "e_home", "e_away", "p_home", "p_draw", "p_away"):
            assert f in r


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
