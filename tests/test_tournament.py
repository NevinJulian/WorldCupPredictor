"""Unit tests for the simulator's match-model interface: team_strength() and the
ratings-free simulate_tournament/_knockout signature. Synthetic, no network. Run: pytest -q
"""
import math
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import models, tournament  # noqa: E402


# --------------------------------------------------------------------------- #
# team_strength on each match model
# --------------------------------------------------------------------------- #
def test_elo_match_model_team_strength_and_default():
    m = tournament.EloMatchModel({"A": 1700.0, "B": 1500.0, "C": 1300.0})
    assert m.team_strength("A") == 1700.0
    assert m.strength_scale == 400.0
    # Unknown team -> the median rating (default_rating), not a KeyError.
    assert m.team_strength("Z") == pytest.approx(float(np.median([1700.0, 1500.0, 1300.0])))


def test_dixon_coles_team_strength_orders_by_skill():
    rng = np.random.default_rng(0)
    teams = ["Strong", "Mid", "Weak"]
    skill = {"Strong": 3.0, "Mid": 1.5, "Weak": 0.6}
    rows, date = [], pd.Timestamp("2015-01-01")
    for _ in range(300):
        date += pd.Timedelta(days=3)
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({"date": date, "home_team": h, "away_team": a,
                     "home_score": int(rng.poisson(skill[h])), "away_score": int(rng.poisson(skill[a])),
                     "tournament": "Friendly", "neutral": True})
    model = models.DixonColesModel().fit(pd.DataFrame(rows))
    assert model.team_strength("Strong") > model.team_strength("Mid") > model.team_strength("Weak")
    assert model.strength_scale == pytest.approx(math.log(10.0))
    # Unseen team -> 0 (league average in the centred parameterisation), no crash.
    assert model.team_strength("Ghost") == 0.0


def _groups12(teams):
    """12 groups A-L of 4 from 48 team names — the real 2026 format the simulator requires."""
    return pd.DataFrame({"group": [chr(ord("A") + i // 4) for i in range(48)], "team": list(teams)})


# --------------------------------------------------------------------------- #
# simulate_tournament with the real Annex-C bracket
# --------------------------------------------------------------------------- #
def test_simulate_tournament_runs_and_is_monotone():
    teams = [f"T{i}" for i in range(48)]
    model = tournament.EloMatchModel({t: 1500 + 5 * i for i, t in enumerate(teams)})
    odds = tournament.simulate_tournament(_groups12(teams), model, n_sims=300, seed=1)
    assert len(odds) == 48
    assert odds["Winner"].sum() == pytest.approx(1.0, abs=0.05)    # one champion per sim
    assert odds["advance"].sum() == pytest.approx(32.0, abs=1e-9)  # 32 qualifiers per sim
    # advance >= R16 >= QF >= SF >= Final >= Winner for every team (nested rounds).
    for a, b in [("advance", "R16"), ("R16", "QF"), ("QF", "SF"), ("SF", "Final"), ("Final", "Winner")]:
        assert (odds[a] >= odds[b]).all()


def test_simulate_tournament_rejects_non_12_group_input():
    groups = pd.DataFrame({"group": ["A"] * 4 + ["B"] * 4, "team": [f"T{i}" for i in range(8)]})
    with pytest.raises(ValueError):
        tournament.simulate_tournament(groups, tournament.EloMatchModel({}), n_sims=1)


def test_dominant_team_wins_far_more_than_uniform():
    # A vastly stronger team must win the title far more often than a uniform 1/48 ~ 0.02.
    teams = [f"T{i}" for i in range(48)]
    ratings = {t: 1500.0 for t in teams}
    ratings["T0"] = 2300.0
    odds = tournament.simulate_tournament(_groups12(teams), tournament.EloMatchModel(ratings), n_sims=400, seed=2)
    assert odds.set_index("team")["Winner"]["T0"] > 0.25


# --------------------------------------------------------------------------- #
# Annex-C round-of-32 slotting
# --------------------------------------------------------------------------- #
def test_annexc_table_is_valid():
    table = tournament.load_annexc()
    assert len(table) == 495
    allowed = {"A": set("CEFHI"), "B": set("EFGIJ"), "D": set("BEFIJ"), "E": set("ABCDF"),
               "G": set("AEHIJ"), "I": set("CDFGH"), "K": set("DEIJL"), "L": set("EHIJK")}
    for combo, assign in table.items():
        assert len(combo) == 8
        assert set(assign.values()) == set(combo)          # bijection onto the qualifying set
        for winner, third in assign.items():
            assert third in allowed[winner]                # respects the published eligibility


def test_r32_matchups_match_published_format_sample():
    # Annex-C row 1: thirds advance from E F G H I J K L. Published slotting (column order
    # 1A,1B,1D,1E,1G,1I,1K,1L) = 3E,3J,3I,3F,3H,3G,3L,3K.
    winners = {g: "1" + g for g in "ABCDEFGHIJKL"}
    runners = {g: "2" + g for g in "ABCDEFGHIJKL"}
    thirds = {g: "3" + g for g in "EFGHIJKL"}
    expected = [("1E", "3F"), ("1I", "3G"), ("2A", "2B"), ("1F", "2C"), ("1C", "2F"), ("2E", "2I"),
                ("1A", "3E"), ("1L", "3K"), ("2K", "2L"), ("1H", "2J"), ("1D", "3I"), ("1G", "3H"),
                ("1J", "2H"), ("2D", "2G"), ("1B", "3J"), ("1K", "3L")]
    assert tournament.r32_matchups(winners, runners, thirds) == expected


def test_no_r32_tie_is_a_same_group_rematch():
    # Across all 495 combinations, no R32 tie pairs two teams from the same group
    # (group = the trailing letter of the sentinel name) — the table is built to avoid it.
    winners = {g: "1" + g for g in "ABCDEFGHIJKL"}
    runners = {g: "2" + g for g in "ABCDEFGHIJKL"}
    for combo in tournament.load_annexc():
        thirds = {g: "3" + g for g in combo}
        for a, b in tournament.r32_matchups(winners, runners, thirds):
            assert a[-1] != b[-1], (sorted(combo), a, b)
