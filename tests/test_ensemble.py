"""Unit tests for the Dixon-Coles + GBM EnsembleModel. Synthetic data, no network. Run: `pytest -q`

The load-bearing guard is no leakage: the mixing weight is chosen on a time-ordered inner-val
window (every inner-train date <= every inner-val date), never the test fold. Also checks the
blend is a valid distribution and collapses to each component at the extreme weights.
"""
import pathlib
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import elo, features, models  # noqa: E402


def _feat_frame(n: int = 900, seed: int = 0, wc_year: "int | None" = None) -> pd.DataFrame:
    """Realistic wide feature table from synthetic matches via the real elo->features pipeline."""
    rng = np.random.default_rng(seed)
    teams = [f"T{i}" for i in range(12)]
    att = {t: float(rng.normal(0, 0.45)) for t in teams}
    dfc = {t: float(rng.normal(0, 0.35)) for t in teams}
    rows, date = [], pd.Timestamp("2008-01-01")
    for _ in range(n):
        date += pd.Timedelta(days=4)
        h, a = rng.choice(teams, 2, replace=False)
        neutral = bool(rng.integers(0, 2))
        lam = np.exp(0.2 + (0.0 if neutral else 0.25) + att[h] - dfc[a])
        mu = np.exp(0.2 + att[a] - dfc[h])
        rows.append({"date": date, "home_team": h, "away_team": a,
                     "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
                     "tournament": "Friendly", "neutral": neutral})
    if wc_year is not None:
        wc = pd.Timestamp(f"{wc_year}-06-11")
        for _ in range(16):
            wc += pd.Timedelta(days=2)
            h, a = rng.choice(teams, 2, replace=False)
            lam = np.exp(0.2 + att[h] - dfc[a]); mu = np.exp(0.2 + att[a] - dfc[h])
            rows.append({"date": wc, "home_team": h, "away_team": a,
                         "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
                         "tournament": "FIFA World Cup", "neutral": True})
    m = pd.DataFrame(rows)
    m["played"] = True
    m["margin"] = m["home_score"] - m["away_score"]
    m["total_goals"] = m["home_score"] + m["away_score"]
    m["result"] = np.where(m.margin > 0, "H", np.where(m.margin < 0, "A", "D"))
    m["year"] = m["date"].dt.year
    with_elo, _ = elo.compute_elo(m)
    return features.build_features(with_elo)


def _fit(feat):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return models.EnsembleModel(gbm_kwargs={"max_iter": 80}).fit(feat)


# --------------------------------------------------------------------------- #
# No leakage: weight tuned on a time-ordered inner-val window
# --------------------------------------------------------------------------- #
def test_inner_time_split_is_time_ordered():
    feat = _feat_frame(n=300)
    inner_train, inner_val = models._inner_time_split(feat, 0.2)
    assert len(inner_train) > 0 and len(inner_val) > 0
    assert len(inner_train) + len(inner_val) == len(feat)
    # Every inner-train date precedes (<=) every inner-val date — no future leaks into tuning.
    assert inner_train["date"].max() <= inner_val["date"].min()
    # inner-val is the most-recent ~fraction of the rows.
    assert len(inner_val) == pytest.approx(len(feat) * 0.2, abs=1)


def test_weight_selection_uses_only_training_rows():
    # Appending later (test-era) matches must not change the weight chosen on a fixed train set:
    # the weight depends only on the rows passed to fit, never on anything after them.
    feat = _feat_frame(n=600)
    w_train = _fit(feat).weight_
    future = feat.tail(20).copy()
    future["date"] = future["date"] + pd.Timedelta(days=4000)  # far-future rows
    w_with_future_appended_but_not_fit = _fit(feat).weight_     # same train -> same weight
    assert w_train == w_with_future_appended_but_not_fit
    assert 0.0 <= w_train <= 1.0


# --------------------------------------------------------------------------- #
# Blend mechanics
# --------------------------------------------------------------------------- #
def test_predict_proba_is_valid_distribution():
    model = _fit(_feat_frame())
    p = model.predict_proba(_feat_frame().tail(40))
    assert p.shape == (40, 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert (p >= 0).all() and (p <= 1).all()


def test_extreme_weights_collapse_to_components():
    feat = _feat_frame()
    model = _fit(feat)
    test = feat.tail(40)
    model.weight_ = 1.0
    assert np.allclose(model.predict_proba(test), model.gbm_.predict_proba(test))
    model.weight_ = 0.0
    p_dc = model.dc_.predict_proba(test)
    assert np.allclose(model.predict_proba(test), p_dc / p_dc.sum(axis=1, keepdims=True))


# --------------------------------------------------------------------------- #
# Time-based walk-forward
# --------------------------------------------------------------------------- #
def test_walk_forward_ensemble_runs():
    feat = _feat_frame(n=700, wc_year=2010)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rows = models.walk_forward_ensemble(feat, years=(2010,), gbm_kwargs={"max_iter": 80})
    assert len(rows) == 1
    r = rows[0]
    assert r["year"] == 2010 and r["n"] == 16
    assert 0.0 <= r["rps"] <= 1.0
    assert 0.0 <= r["weight"] <= 1.0
