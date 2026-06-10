"""Unit tests for wcpred.metrics — pin the RPS normalization convention. Run: `pytest -q`

The headline guard: a perfect confident forecast scores 0, and a hand-computed case
matches the STANDARD normalized RPS formula (divide by r-1 = 2). The old notebook helper
dropped that factor; these tests make sure we never silently drift back to it.
"""
import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import metrics  # noqa: E402


# --------------------------------------------------------------------------- #
# RPS — normalization is the whole point
# --------------------------------------------------------------------------- #
def test_rps_perfect_confident_forecast_is_zero():
    # All mass on the realized outcome -> 0 in any convention.
    assert metrics.rps([[1.0, 0.0, 0.0]], [0]) == pytest.approx(0.0)
    assert metrics.rps([[0.0, 1.0, 0.0]], [1]) == pytest.approx(0.0)
    assert metrics.rps([[0.0, 0.0, 1.0]], [2]) == pytest.approx(0.0)


def test_rps_hand_computed_normalized_case():
    # p=[0.5,0.3,0.2], outcome = Home (class 0). Cumulative diffs:
    #   (0.5-1)^2 + (0.8-1)^2 = 0.25 + 0.04 = 0.29 ; normalized / (r-1)=2 -> 0.145
    # (The un-normalized notebook helper would have returned 0.29 — exactly 2x.)
    assert metrics.rps([[0.5, 0.3, 0.2]], [0]) == pytest.approx(0.145)


def test_rps_accepts_string_labels():
    # 'H' must resolve to class 0 and give the same hand-computed value.
    assert metrics.rps([[0.5, 0.3, 0.2]], ["H"]) == pytest.approx(0.145)


def test_rps_worst_case_is_one():
    # All mass on the far-wrong extreme: p=[0,0,1], outcome = Home -> normalized worst = 1.
    assert metrics.rps([[0.0, 0.0, 1.0]], [0]) == pytest.approx(1.0)


def test_rps_is_mean_over_matches():
    p = [[0.5, 0.3, 0.2], [1.0, 0.0, 0.0]]
    y = [0, 0]
    assert metrics.rps(p, y) == pytest.approx((0.145 + 0.0) / 2)


def test_rps_per_match_returns_vector_and_means_to_rps():
    p = [[0.5, 0.3, 0.2], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
    y = [0, 0, 0]
    per = metrics.rps_per_match(p, y)
    assert per.shape == (3,)
    assert per[0] == pytest.approx(0.145)   # hand case
    assert per[1] == pytest.approx(0.0)     # perfect confident
    assert per[2] == pytest.approx(1.0)     # worst case
    assert per.mean() == pytest.approx(metrics.rps(p, y))


def test_rps_rewards_ordinal_closeness():
    # Outcome = Away. Putting the wrong mass on Draw (adjacent) must beat putting it on
    # Home (far) — this is the property log-loss/Brier can't see.
    near = metrics.rps([[0.0, 0.5, 0.5]], [2])
    far = metrics.rps([[0.5, 0.0, 0.5]], [2])
    assert near < far


# --------------------------------------------------------------------------- #
# Log-loss & Brier — hand values
# --------------------------------------------------------------------------- #
def test_log_loss_perfect_is_zero():
    assert metrics.multiclass_log_loss([[1.0, 0.0, 0.0]], [0]) == pytest.approx(0.0, abs=1e-9)


def test_log_loss_hand_value():
    # Single sample, probability on the realized class is 0.5 -> -ln(0.5).
    assert metrics.multiclass_log_loss([[0.5, 0.3, 0.2]], [0]) == pytest.approx(-np.log(0.5))


def test_brier_hand_value():
    # p=[0.5,0.3,0.2], o=[1,0,0] -> 0.25 + 0.09 + 0.04 = 0.38
    assert metrics.brier([[0.5, 0.3, 0.2]], [0]) == pytest.approx(0.38)


def test_brier_perfect_is_zero():
    assert metrics.brier([[0.0, 1.0, 0.0]], [1]) == pytest.approx(0.0)


# --------------------------------------------------------------------------- #
# Calibration table
# --------------------------------------------------------------------------- #
def test_calibration_table_perfect_extremes():
    # Two confident, correct forecasts: every predicted-1.0 point is a hit, every
    # predicted-0.0 point is a miss -> top bin observed_freq 1.0, bottom bin 0.0.
    p = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    y = [0, 1]
    tbl = metrics.calibration_table(p, y, n_bins=10)
    top = tbl[tbl["bin_upper"] == 1.0].iloc[0]
    bottom = tbl[tbl["bin_lower"] == 0.0].iloc[0]
    assert top["observed_freq"] == pytest.approx(1.0)
    assert top["mean_pred"] == pytest.approx(1.0)
    assert bottom["observed_freq"] == pytest.approx(0.0)
    # Pooled over 2 samples x 3 classes = 6 points total.
    assert int(tbl["count"].sum()) == 6


def test_metrics_handle_batches():
    # Shape-sanity over a small batch with mixed outcomes; all metrics return finite scalars.
    rng = np.random.default_rng(0)
    p = rng.dirichlet([1, 1, 1], size=50)
    y = rng.integers(0, 3, size=50)
    for fn in (metrics.rps, metrics.multiclass_log_loss, metrics.brier):
        val = fn(p, y)
        assert np.isfinite(val) and val >= 0.0
