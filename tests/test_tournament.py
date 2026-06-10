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


# --------------------------------------------------------------------------- #
# simulate_tournament without the ratings dict
# --------------------------------------------------------------------------- #
def test_simulate_tournament_runs_without_ratings_dict():
    groups = pd.DataFrame({"group": ["A"] * 4 + ["B"] * 4,
                           "team": ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]})
    model = tournament.EloMatchModel({t: 1500 + 40 * i for i, t in enumerate(groups["team"])})
    odds = tournament.simulate_tournament(groups, model, n_sims=200, seed=1)
    assert len(odds) == 8
    assert (odds["advance"] <= 1.0).all()
    assert odds["Winner"].sum() == pytest.approx(1.0, abs=0.05)   # exactly one champion per sim


def test_knockout_seeding_favours_the_strongest_team():
    # A vastly stronger team must win the title far more often than a uniform 1/8.
    groups = pd.DataFrame({"group": ["A"] * 4 + ["B"] * 4,
                           "team": ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4"]})
    ratings = {t: 1500.0 for t in groups["team"]}
    ratings["A1"] = 2200.0
    odds = tournament.simulate_tournament(groups, tournament.EloMatchModel(ratings), n_sims=400, seed=2)
    assert odds.set_index("team")["Winner"]["A1"] > 0.25
