"""Train/test construction — always time-based, never random.

The cardinal rule of sports modelling: evaluate the way you'll actually use the model —
predicting the future from the past. Random K-fold leaks the future and flatters your score.
"""
from __future__ import annotations

from typing import Iterator

import pandas as pd

from .elo import K_FRIENDLY, K_QUALIFIER, k_for_tournament

RESULT_TO_INT = {"H": 0, "D": 1, "A": 2}


def played_only(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["played"]].copy()


# --------------------------------------------------------------------------- #
# Competitiveness tiers — for the broadened evaluation
# --------------------------------------------------------------------------- #
def competition_class(df: pd.DataFrame) -> pd.Series:
    """Classify each match by competitiveness tier from its ``tournament`` label.

    Three tiers, derived from the Elo importance K-factor (``elo.k_for_tournament``) so the
    eval slices line up exactly with how the ratings already weight matches:

    * ``"competitive"`` — qualifiers + continental championships + World Cup finals
      (K >= 40). This is the **sensitive detector**: it has far more matches than the WC
      finals alone, yet excludes the noisy friendlies. Literature reference ~0.165 RPS
      (Ley et al. 2019).
    * ``"friendly"`` — friendlies (K == 20). Noisier; reported but never optimised on.
    * ``"other"`` — minor / regional competitions (K == 30, e.g. Nations League, regional
      cups). Neither clearly competitive nor a friendly; kept out of both headline slices.

    Returns a string Series aligned to ``df.index``.
    """
    k = df["tournament"].map(k_for_tournament)
    cls = pd.Series("other", index=df.index, dtype=object)
    cls[k >= K_QUALIFIER] = "competitive"
    cls[k == K_FRIENDLY] = "friendly"
    return cls


def is_competitive(df: pd.DataFrame) -> pd.Series:
    """Boolean mask for the competitive tier (qualifiers + continental + WC finals)."""
    return competition_class(df) == "competitive"


def walk_forward_blocks(
    df: pd.DataFrame, years: range, *, min_train: int = 2000
) -> Iterator[tuple[int, pd.DataFrame, pd.DataFrame]]:
    """Yield (checkpoint_year, train, block) for an expanding-window block backtest.

    For each ``year`` in ``years`` the model is meant to be refit on ``train`` — every PLAYED
    match dated strictly before Jan 1 of ``year`` — and scored on ``block`` — every PLAYED
    match in ``[year, year+1)``. So each block is predicted only from matches that finished
    before it began (as-of / no leakage by construction), and the blocks tile the span with
    no overlap and no gaps. Folds whose training set is smaller than ``min_train`` (the early,
    data-starved years) are skipped.
    """
    played = played_only(df)
    for year in years:
        lo = pd.Timestamp(f"{year}-01-01")
        hi = pd.Timestamp(f"{year + 1}-01-01")
        train = played[played["date"] < lo]
        block = played[(played["date"] >= lo) & (played["date"] < hi)]
        if len(train) < min_train or block.empty:
            continue
        yield year, train.copy(), block.copy()


def time_split(df: pd.DataFrame, cutoff: str | pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train on matches before `cutoff`, test on/after it."""
    cutoff = pd.Timestamp(cutoff)
    df = played_only(df)
    return df[df["date"] < cutoff].copy(), df[df["date"] >= cutoff].copy()


def is_world_cup_finals(df: pd.DataFrame) -> pd.Series:
    """World Cup finals matches (not qualifiers)."""
    t = df["tournament"].astype(str).str.lower()
    return t.str.contains("fifa world cup") & ~t.str.contains("qualif")


def tournament_holdout(df: pd.DataFrame, year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train on everything before that World Cup; test = that World Cup's finals matches.

    This is the headline backtest: it mimics standing on the eve of the tournament.
    """
    df = played_only(df)
    wc = is_world_cup_finals(df) & (df["year"] == year)
    test = df[wc].copy()
    if test.empty:
        raise ValueError(f"No World Cup finals matches found for {year}.")
    start = test["date"].min()
    train = df[df["date"] < start].copy()
    return train, test


def walk_forward_tournaments(
    df: pd.DataFrame, years: tuple[int, ...] = (2010, 2014, 2018, 2022)
) -> Iterator[tuple[int, pd.DataFrame, pd.DataFrame]]:
    """Yield (year, train, test) for each World Cup — expanding training window."""
    for y in years:
        try:
            train, test = tournament_holdout(df, y)
        except ValueError:
            continue
        yield y, train, test


def xy_outcome(df: pd.DataFrame, feature_cols: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Features X and integer outcome target y (0=H, 1=D, 2=A)."""
    X = df[feature_cols].copy()
    y = df["result"].map(RESULT_TO_INT).astype("Int64")
    return X, y


def xy_goals(df: pd.DataFrame, feature_cols: list[str]) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Features X and the two goal targets (home_score, away_score) for the Poisson model."""
    X = df[feature_cols].copy()
    return X, df["home_score"].copy(), df["away_score"].copy()
