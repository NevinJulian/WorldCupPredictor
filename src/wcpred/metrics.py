"""Probabilistic-forecast metrics for the 1X2 (H/D/A) match model.

The primary metric is the **Ranked Probability Score (RPS)** — unlike log-loss and
Brier, it respects the natural ordering Home > Draw > Away (being one goal off in the
right direction beats being two off). We use the STANDARD *normalized* RPS:

    RPS = 1/(r-1) * sum_{i=1}^{r-1} ( sum_{j<=i} (p_j - o_j) )^2

for ``r`` ordered categories (here r=3, so the normalizer is r-1 = 2). Normalizing
puts the score on a 0..1 scale — a perfect confident forecast is 0, the worst possible
forecast is 1 — and makes it comparable across different numbers of categories.

NOTE: an earlier notebook helper omitted the ``1/(r-1)`` factor, so any RPS quoted from
it is 2x the values produced here. In this (correct) normalized convention the pure-Elo
baseline scores per-WC 0.1965 / 0.1848 / 0.2105 / 0.2262, avg **0.2045**.

Class order is the project convention H, D, A (see ``datasets.RESULT_TO_INT``:
0=H, 1=D, 2=A); RPS treats the probability columns as ordinal in that left-to-right
order. All functions accept ``y_true`` as integer class indices OR 'H'/'D'/'A' strings.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Kept in sync with datasets.RESULT_TO_INT — duplicated here to avoid a circular import.
RESULT_TO_INT = {"H": 0, "D": 1, "A": 2}


# --------------------------------------------------------------------------- #
# Input coercion
# --------------------------------------------------------------------------- #
def _as_prob_matrix(y_prob) -> np.ndarray:
    """Coerce forecasts to a 2-D (n, r) float array; a single forecast becomes one row."""
    p = np.asarray(y_prob, dtype=float)
    if p.ndim == 1:
        p = p.reshape(1, -1)
    if p.ndim != 2:
        raise ValueError(f"y_prob must be 1-D or 2-D, got shape {p.shape}")
    return p


def _as_labels(y_true, n_classes: int) -> np.ndarray:
    """Coerce ``y_true`` to a 1-D int array of class indices (accepts H/D/A strings)."""
    arr = np.asarray(y_true)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.dtype.kind in ("U", "S", "O"):
        arr = np.array([RESULT_TO_INT[str(v)] for v in arr])
    arr = arr.astype(int)
    if arr.size and (arr.min() < 0 or arr.max() >= n_classes):
        raise ValueError(f"labels out of range for {n_classes} classes: {np.unique(arr)}")
    return arr


def _one_hot(labels: np.ndarray, n_classes: int) -> np.ndarray:
    oh = np.zeros((len(labels), n_classes), dtype=float)
    oh[np.arange(len(labels)), labels] = 1.0
    return oh


def _check_aligned(p: np.ndarray, labels: np.ndarray) -> None:
    if len(p) != len(labels):
        raise ValueError(f"y_prob has {len(p)} rows but y_true has {len(labels)}")


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def rps(y_prob, y_true) -> float:
    """Mean **normalized** Ranked Probability Score (lower is better; range 0..1).

    Parameters
    ----------
    y_prob : array-like, shape (n, r)
        Forecast probabilities, columns ordered H, D, A.
    y_true : array-like, shape (n,)
        Realized outcomes as class indices (0=H, 1=D, 2=A) or 'H'/'D'/'A' strings.
    """
    p = _as_prob_matrix(y_prob)
    r = p.shape[1]
    labels = _as_labels(y_true, r)
    _check_aligned(p, labels)
    o = _one_hot(labels, r)

    cum_p = np.cumsum(p, axis=1)
    cum_o = np.cumsum(o, axis=1)
    # The r-th cumulative difference is always 0 (both rows sum to 1), so the standard
    # sum runs i = 1..r-1. Slicing the last column off also makes us independent of any
    # tiny float drift in the final cumulative sum. Normalize by (r - 1).
    per_match = ((cum_p[:, :-1] - cum_o[:, :-1]) ** 2).sum(axis=1) / (r - 1)
    return float(per_match.mean())


def multiclass_log_loss(y_prob, y_true, eps: float = 1e-15) -> float:
    """Mean multiclass cross-entropy in nats (natural log; lower is better)."""
    p = _as_prob_matrix(y_prob)
    r = p.shape[1]
    labels = _as_labels(y_true, r)
    _check_aligned(p, labels)

    p = np.clip(p, eps, 1.0)
    p = p / p.sum(axis=1, keepdims=True)  # renormalize after clipping
    picked = p[np.arange(len(labels)), labels]
    return float(-np.log(picked).mean())


def brier(y_prob, y_true) -> float:
    """Mean multiclass Brier score: mean over samples of ``sum_k (p_k - o_k)^2`` (range 0..2)."""
    p = _as_prob_matrix(y_prob)
    r = p.shape[1]
    labels = _as_labels(y_true, r)
    _check_aligned(p, labels)
    o = _one_hot(labels, r)
    return float(((p - o) ** 2).sum(axis=1).mean())


def calibration_table(y_prob, y_true, n_bins: int = 10) -> pd.DataFrame:
    """Reliability table pooled across all classes (one-vs-rest).

    Each (sample, class) pair contributes a (predicted probability, hit) point; points are
    binned by predicted probability into ``n_bins`` equal-width bins over [0, 1]. A
    well-calibrated model has ``mean_pred ~= observed_freq`` in every bin.

    Returns one row per non-empty bin with columns:
        bin_lower, bin_upper, bin_mid, count, mean_pred, observed_freq
    """
    p = _as_prob_matrix(y_prob)
    r = p.shape[1]
    labels = _as_labels(y_true, r)
    _check_aligned(p, labels)
    o = _one_hot(labels, r)

    pred = p.ravel()
    hit = o.ravel()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # digitize -> 1..n_bins; shift to 0-based and fold the closed right edge (p==1) into
    # the last bin so a confident, correct forecast lands in [.9, 1.0], not its own bin.
    idx = np.clip(np.digitize(pred, edges, right=False) - 1, 0, n_bins - 1)

    rows = []
    for b in range(n_bins):
        mask = idx == b
        count = int(mask.sum())
        if count == 0:
            continue
        rows.append({
            "bin_lower": float(edges[b]),
            "bin_upper": float(edges[b + 1]),
            "bin_mid": float((edges[b] + edges[b + 1]) / 2),
            "count": count,
            "mean_pred": float(pred[mask].mean()),
            "observed_freq": float(hit[mask].mean()),
        })
    return pd.DataFrame(rows, columns=[
        "bin_lower", "bin_upper", "bin_mid", "count", "mean_pred", "observed_freq",
    ])
