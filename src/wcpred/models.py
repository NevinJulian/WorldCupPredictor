"""Match-outcome (and later goals) models.

This module starts with the **baseline** the whole project is measured against (PLAN.md §7):

    EloLogisticModel — a multinomial logistic regression on just `elo_diff` and the
    neutral-venue flag. It is deliberately minimal. The point of a baseline is to be the
    bar a fancier model must clear, not to be a contender, so it gets exactly two inputs:
    the single most predictive feature (Elo difference) plus whether the venue is neutral.

`walk_forward_elo_baseline` fits and scores it the only way we evaluate anything here —
time-based, training strictly before each World Cup (see datasets.walk_forward_tournaments)
— and returns the per-tournament normalized RPS that later models must beat.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from . import datasets, metrics

# The baseline's entire feature set. Order matters only for the design matrix layout.
BASELINE_FEATURES: tuple[str, ...] = ("elo_diff", "neutral")
DEFAULT_WC_YEARS: tuple[int, ...] = (2010, 2014, 2018, 2022)


class EloLogisticModel:
    """Multinomial logistic P(H/D/A) from `elo_diff` + `neutral`. The bar to beat.

    Predicts a full H/D/A distribution (columns ordered 0=H, 1=D, 2=A, matching
    datasets.RESULT_TO_INT). This is an *outcome* model; it does not implement the
    simulator's `sample_scoreline` goals interface.
    """

    def __init__(self, max_iter: int = 2000):
        self.max_iter = max_iter
        self.clf = LogisticRegression(max_iter=max_iter)

    def _design(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build the two-column design matrix. NaN elo_diff -> 0 (as in the baseline notebook)."""
        return pd.DataFrame({
            "elo_diff": pd.to_numeric(df["elo_diff"], errors="coerce").fillna(0.0).astype(float).to_numpy(),
            "neutral": df["neutral"].astype(int).to_numpy(),
        })

    def fit(self, df: pd.DataFrame) -> "EloLogisticModel":
        X = self._design(df)
        y = df["result"].map(datasets.RESULT_TO_INT).astype(int)
        self.clf.fit(X, y)
        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Return an (n, 3) array of P(H/D/A), columns always in H,D,A order.

        Re-indexes the classifier's columns into fixed 0,1,2 positions so the output is
        well-defined even if a class was absent from a (tiny) training fold.
        """
        proba = self.clf.predict_proba(self._design(df))
        full = np.zeros((len(df), 3), dtype=float)
        for j, c in enumerate(self.clf.classes_):
            full[:, int(c)] = proba[:, j]
        return full


def walk_forward_elo_baseline(
    df: pd.DataFrame, years: tuple[int, ...] = DEFAULT_WC_YEARS
) -> list[dict]:
    """Fit the Elo-logistic baseline per World Cup and score normalized RPS.

    For each year, train on every match strictly before that tournament and test on its
    finals (datasets.walk_forward_tournaments enforces the time-based split — never random).
    Returns one dict per tournament: ``{"year", "n", "rps"}`` with RPS in the standard
    normalized convention (metrics.rps).
    """
    rows: list[dict] = []
    for year, train, test in datasets.walk_forward_tournaments(df, years):
        model = EloLogisticModel().fit(train)
        proba = model.predict_proba(test)
        y_true = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        rows.append({"year": year, "n": int(len(test)), "rps": metrics.rps(proba, y_true)})
    return rows
