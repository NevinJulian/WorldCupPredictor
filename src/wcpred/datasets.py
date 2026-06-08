"""Train/test construction — always time-based, never random.

The cardinal rule of sports modelling: evaluate the way you'll actually use the model —
predicting the future from the past. Random K-fold leaks the future and flatters your score.
"""
from __future__ import annotations

from typing import Iterator

import pandas as pd

RESULT_TO_INT = {"H": 0, "D": 1, "A": 2}


def played_only(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["played"]].copy()


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
