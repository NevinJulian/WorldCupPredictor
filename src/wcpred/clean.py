"""Load and clean the raw match data into a canonical frame.

Output of `load_clean_results()` — one row per match, sorted by date, with:
    date, home_team, away_team, home_score, away_score, tournament, city, country,
    neutral, played, result (H/D/A), margin, total_goals, year
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import DATA_RAW


def _load_former_names(raw_dir: Path) -> dict[str, str]:
    """Map historical country names to their modern equivalent (date ranges ignored —
    fine for team-continuity modelling; revisit if you care about e.g. the German split)."""
    fp = raw_dir / "former_names.csv"
    if not fp.exists():
        return {}
    fn = pd.read_csv(fp)
    return dict(zip(fn["former"].astype(str), fn["current"].astype(str)))


def standardize_names(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    if not mapping:
        return df
    df = df.copy()
    for col in ("home_team", "away_team"):
        df[col] = df[col].replace(mapping)
    return df


def load_clean_results(raw_dir: Path | None = None, apply_former_names: bool = False) -> pd.DataFrame:
    """Read results.csv and return the canonical, cleaned match frame."""
    raw_dir = raw_dir or DATA_RAW
    fp = raw_dir / "results.csv"
    if not fp.exists():
        raise FileNotFoundError(
            f"{fp} not found. Run `python scripts/01_download.py` first."
        )

    df = pd.read_csv(fp)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_team", "away_team"])

    for c in ("home_score", "away_score"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # `neutral` may arrive as bool or string.
    df["neutral"] = (
        df["neutral"].astype(str).str.lower().isin(["true", "1", "yes"])
        if df["neutral"].dtype == object
        else df["neutral"].astype(bool)
    )

    if apply_former_names:
        df = standardize_names(df, _load_former_names(raw_dir))

    df["played"] = df["home_score"].notna() & df["away_score"].notna()
    df["margin"] = df["home_score"] - df["away_score"]
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["result"] = np.where(
        df["margin"] > 0, "H", np.where(df["margin"] < 0, "A", "D")
    )
    df.loc[~df["played"], "result"] = np.nan
    df["year"] = df["date"].dt.year

    df = df.sort_values("date", kind="stable").reset_index(drop=True)
    return df


def to_long(matches: pd.DataFrame) -> pd.DataFrame:
    """Team-perspective ('long') view: two rows per match. Used for rolling form."""
    home = matches.assign(
        team=matches["home_team"], opponent=matches["away_team"],
        is_home=True, gf=matches["home_score"], ga=matches["away_score"],
    )
    away = matches.assign(
        team=matches["away_team"], opponent=matches["home_team"],
        is_home=False, gf=matches["away_score"], ga=matches["home_score"],
    )
    long = pd.concat([home, away], ignore_index=True)
    # Points from the team's own perspective.
    long["points"] = np.select(
        [long["gf"] > long["ga"], long["gf"] == long["ga"]], [3, 1], default=0
    ).astype(float)
    long.loc[long["gf"].isna(), "points"] = np.nan
    return long.sort_values(["date"], kind="stable").reset_index(drop=True)
