"""Unit tests for wcpred.models — the Elo-logistic baseline. Synthetic data, no network.

Guards the two things that matter for a baseline: it produces a valid, correctly-ordered
H/D/A distribution, and it is scored time-based (train strictly before the test tournament,
never a random split).
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import datasets, models  # noqa: E402


def _fit_frame(n: int = 400) -> pd.DataFrame:
    """A frame with all three outcomes correlated with elo_diff (so every class is present)."""
    rng = np.random.default_rng(1)
    elo_diff = rng.normal(0, 150, n)
    neutral = rng.integers(0, 2, n).astype(bool)
    result = np.where(elo_diff > 70, "H", np.where(elo_diff < -70, "A", "D"))
    return pd.DataFrame({"elo_diff": elo_diff, "neutral": neutral, "result": result})


def _walk_forward_frame() -> pd.DataFrame:
    """Friendlies 2006-2009 (training pool) + a small FIFA World Cup 2010 (the test fold)."""
    rng = np.random.default_rng(0)
    teams = ["A", "B", "C", "D"]
    rows = []

    date = pd.Timestamp("2006-01-01")
    for _ in range(80):
        date += pd.Timedelta(days=14)
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({
            "date": date, "home_team": h, "away_team": a, "tournament": "Friendly",
            "neutral": False, "elo_diff": float(rng.normal(0, 200)),
            "result": rng.choice(["H", "D", "A"], p=[0.45, 0.27, 0.28]),
        })

    wc = pd.Timestamp("2010-06-11")
    for _ in range(8):
        wc += pd.Timedelta(days=2)
        h, a = rng.choice(teams, 2, replace=False)
        rows.append({
            "date": wc, "home_team": h, "away_team": a, "tournament": "FIFA World Cup",
            "neutral": True, "elo_diff": float(rng.normal(0, 200)),
            "result": rng.choice(["H", "D", "A"], p=[0.45, 0.27, 0.28]),
        })

    df = pd.DataFrame(rows)
    df["played"] = True
    df["year"] = df["date"].dt.year
    return df


# --------------------------------------------------------------------------- #
# Model mechanics
# --------------------------------------------------------------------------- #
def test_predict_proba_is_valid_distribution():
    df = _fit_frame()
    p = models.EloLogisticModel().fit(df).predict_proba(df)
    assert p.shape == (len(df), 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert (p >= 0).all() and (p <= 1).all()


def test_higher_elo_diff_raises_home_prob():
    # P(home win) must increase with elo_diff — the baseline's whole premise.
    model = models.EloLogisticModel().fit(_fit_frame())
    lo = model.predict_proba(pd.DataFrame({"elo_diff": [-300.0], "neutral": [0]}))[0, 0]
    hi = model.predict_proba(pd.DataFrame({"elo_diff": [300.0], "neutral": [0]}))[0, 0]
    assert hi > lo


def test_model_uses_only_elo_diff_and_neutral():
    # A frame with ONLY the two baseline inputs (+ target) must fit and predict — the model
    # must not depend on any other feature column.
    df = _fit_frame()[["elo_diff", "neutral", "result"]]
    p = models.EloLogisticModel().fit(df).predict_proba(df)
    assert p.shape[1] == 3
    assert tuple(models.BASELINE_FEATURES) == ("elo_diff", "neutral")


# --------------------------------------------------------------------------- #
# Time-based evaluation (no leakage)
# --------------------------------------------------------------------------- #
def test_holdout_train_is_strictly_before_test():
    train, test = datasets.tournament_holdout(_walk_forward_frame(), 2010)
    assert train["date"].max() < test["date"].min()
    assert test["tournament"].str.contains("World Cup").all()
    assert len(train) > 0


def test_walk_forward_baseline_scores_each_tournament():
    rows = models.walk_forward_elo_baseline(_walk_forward_frame(), years=(2010,))
    assert len(rows) == 1
    r = rows[0]
    assert r["year"] == 2010 and r["n"] == 8
    assert 0.0 <= r["rps"] <= 1.0  # normalized RPS is on [0, 1]
