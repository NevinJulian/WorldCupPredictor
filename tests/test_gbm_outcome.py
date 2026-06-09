"""Unit tests for the gradient-boosted outcome model. Synthetic data, no network. Run: `pytest -q`

Guards: the model feeds on the FULL feature set (absolute home_*/away_* + diffs + form
windows, NOT diff-only) with targets/context excluded, produces a valid isotonic-calibrated
H/D/A distribution, and is scored time-based via walk_forward.
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
    """Build a realistic wide feature table from synthetic matches via the real pipeline."""
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
        rows.append({
            "date": date, "home_team": h, "away_team": a,
            "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
            "tournament": "Friendly", "neutral": neutral,
        })
    if wc_year is not None:
        wc = pd.Timestamp(f"{wc_year}-06-11")
        for _ in range(16):
            wc += pd.Timedelta(days=2)
            h, a = rng.choice(teams, 2, replace=False)
            lam = np.exp(0.2 + att[h] - dfc[a]); mu = np.exp(0.2 + att[a] - dfc[h])
            rows.append({
                "date": wc, "home_team": h, "away_team": a,
                "home_score": int(rng.poisson(lam)), "away_score": int(rng.poisson(mu)),
                "tournament": "FIFA World Cup", "neutral": True,
            })

    m = pd.DataFrame(rows)
    m["played"] = True
    m["margin"] = m["home_score"] - m["away_score"]
    m["total_goals"] = m["home_score"] + m["away_score"]
    m["result"] = np.where(m.margin > 0, "H", np.where(m.margin < 0, "A", "D"))
    m["year"] = m["date"].dt.year
    with_elo, _ = elo.compute_elo(m)
    return features.build_features(with_elo)


# --------------------------------------------------------------------------- #
# Feature set: full, not diff-only; targets/context excluded
# --------------------------------------------------------------------------- #
def test_gbm_feature_columns_full_not_diff_only():
    fc = set(models.gbm_feature_columns(_feat_frame(n=200)))
    # Absolute home_/away_ columns AND diffs AND a 10-match form window are all present.
    for col in ("elo_home", "elo_away", "elo_diff", "home_form_ppg_10",
                "away_form_ppg_10", "form_ppg_10_diff"):
        assert col in fc, f"expected {col} in the GBM feature set"
    # Not a diff-only subset: some non-diff columns are present.
    assert any(not c.endswith("_diff") for c in fc)


def test_gbm_feature_columns_exclude_targets_and_context():
    fc = set(models.gbm_feature_columns(_feat_frame(n=200)))
    for leak in ("home_score", "away_score", "result", "margin", "total_goals"):
        assert leak not in fc
    # rest/context/host are kept in the pipeline but dropped from the model inputs.
    for ctx in ("home_rest_days", "away_rest_days", "rest_days_diff",
                "home_matches_30d", "matches_30d_diff", "home_is_host", "away_is_host"):
        assert ctx not in fc


# --------------------------------------------------------------------------- #
# Calibrated distribution
# --------------------------------------------------------------------------- #
def test_gbm_predict_proba_is_valid_distribution():
    feat = _feat_frame()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = models.GBMOutcomeModel(max_iter=80).fit(feat)
    p = model.predict_proba(feat.tail(50))
    assert p.shape == (50, 3)
    assert np.allclose(p.sum(axis=1), 1.0)
    assert (p >= 0).all() and (p <= 1).all()


def test_gbm_fit_is_calibrated_and_excludes_targets():
    feat = _feat_frame()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = models.GBMOutcomeModel(max_iter=80).fit(feat)
    assert model.calibrated_ is not None            # isotonic calibrator fitted
    assert model.feature_cols_                        # feature list stored
    assert "result" not in model.feature_cols_        # target never an input (as-of)


# --------------------------------------------------------------------------- #
# Time-based walk-forward
# --------------------------------------------------------------------------- #
def test_walk_forward_gbm_outcome_runs():
    feat = _feat_frame(n=700, wc_year=2010)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rows = models.walk_forward_gbm_outcome(feat, years=(2010,), max_iter=80)
    assert len(rows) == 1
    r = rows[0]
    assert r["year"] == 2010 and r["n"] == 16
    assert 0.0 <= r["rps"] <= 1.0
