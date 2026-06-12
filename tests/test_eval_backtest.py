"""Tests for the broadened block backtest (datasets + models). Synthetic data, no network.

These guard the new, larger evaluator used to sweep the Dixon-Coles half-life:
  * the competitiveness tiers line up with the Elo K-factor (qualifiers + continental + WC =
    competitive; friendlies = friendly; the rest = other);
  * the yearly-checkpoint block backtest is as-of by construction (every block is predicted
    only from matches that finished strictly before it began) and the blocks tile the span
    with no overlap or gaps;
  * the pooled-prediction runner and the RPS-by-tier scorer account correctly.
Run: `pytest -q`
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import datasets  # noqa: E402
from wcpred.models import (  # noqa: E402
    DixonColesModel, block_rps_by_class, walk_forward_block_predictions,
)


# --------------------------------------------------------------------------- #
# Synthetic history
# --------------------------------------------------------------------------- #
_TOURNAMENTS = (
    "Friendly", "FIFA World Cup qualification", "UEFA Euro qualification",
    "UEFA Euro", "FIFA World Cup", "UEFA Nations League",
)


def _multi_year(start: int = 2005, end: int = 2016, per_year: int = 60, seed: int = 7) -> pd.DataFrame:
    """A multi-year played history among 6 teams across several tournament tiers."""
    rng = np.random.default_rng(seed)
    teams = ["A", "B", "C", "D", "E", "F"]
    rows = []
    for year in range(start, end):
        for _ in range(per_year):
            day = int(rng.integers(0, 360))
            h, a = rng.choice(teams, size=2, replace=False)
            hs, as_ = int(rng.integers(0, 4)), int(rng.integers(0, 4))
            rows.append({
                "date": pd.Timestamp(f"{year}-01-01") + pd.Timedelta(days=day),
                "home_team": h, "away_team": a, "home_score": hs, "away_score": as_,
                "neutral": bool(rng.integers(0, 2)),
                "tournament": str(rng.choice(_TOURNAMENTS)), "year": year, "played": True,
            })
    df = pd.DataFrame(rows).sort_values("date", kind="stable").reset_index(drop=True)
    df["result"] = np.where(df.home_score > df.away_score, "H",
                            np.where(df.home_score == df.away_score, "D", "A"))
    return df


# --------------------------------------------------------------------------- #
# competition_class
# --------------------------------------------------------------------------- #
def test_competition_class_tiers():
    df = pd.DataFrame({"tournament": [
        "Friendly",
        "FIFA World Cup qualification",        # qualifier  -> competitive
        "UEFA Euro qualification",             # qualifier  -> competitive
        "UEFA Euro",                           # continental-> competitive
        "Copa América",                        # continental-> competitive
        "FIFA World Cup",                      # WC finals  -> competitive
        "UEFA Nations League",                 # minor (K30)-> other
        "Kirin Cup",                           # minor      -> other
    ]})
    got = list(datasets.competition_class(df))
    assert got == ["friendly", "competitive", "competitive", "competitive",
                   "competitive", "competitive", "other", "other"]
    # is_competitive is the boolean view of the same tier
    assert list(datasets.is_competitive(df)) == [c == "competitive" for c in got]


def test_competition_class_index_aligned():
    df = _multi_year(2005, 2007)
    cls = datasets.competition_class(df)
    assert cls.index.equals(df.index) and set(cls.unique()) <= {"competitive", "friendly", "other"}


# --------------------------------------------------------------------------- #
# walk_forward_blocks — as-of and tiling
# --------------------------------------------------------------------------- #
def test_walk_forward_blocks_are_as_of_and_tile():
    df = _multi_year()
    folds = list(datasets.walk_forward_blocks(df, range(2006, 2016), min_train=50))
    assert folds, "expected at least one usable fold"
    seen_years = []
    for year, train, block in folds:
        lo, hi = pd.Timestamp(f"{year}-01-01"), pd.Timestamp(f"{year + 1}-01-01")
        # As-of: every training match finished strictly before the block opens.
        assert train["date"].max() < lo <= block["date"].min()
        assert block["date"].max() < hi
        assert len(train) >= 50
        # The block is exactly that calendar year's played matches.
        assert (block["year"] == year).all()
        seen_years.append(year)
    # Blocks are disjoint and each covers a distinct year.
    assert len(seen_years) == len(set(seen_years))


def test_walk_forward_blocks_respects_min_train():
    df = _multi_year()
    # A min_train larger than the whole history yields no folds (rather than leaking).
    assert list(datasets.walk_forward_blocks(df, range(2006, 2016), min_train=10_000)) == []


# --------------------------------------------------------------------------- #
# walk_forward_block_predictions — no leakage + accounting
# --------------------------------------------------------------------------- #
class _Recorder:
    """A trivial fixed-probability model that records its training window per fold."""

    def __init__(self, log: list):
        self.log = log
        self._tmax = None

    def fit(self, train: pd.DataFrame) -> "_Recorder":
        self._tmax = train["date"].max()
        return self

    def predict_proba(self, block: pd.DataFrame) -> np.ndarray:
        self.log.append((self._tmax, block["date"].min()))
        return np.tile([0.5, 0.3, 0.2], (len(block), 1))


def test_block_predictions_are_as_of_and_complete():
    df = _multi_year()
    log: list = []
    pooled = walk_forward_block_predictions(df, lambda: _Recorder(log), range(2006, 2016), min_train=50)
    # Every fold trained strictly before its block began (no leakage).
    assert log and all(tmax < bmin for tmax, bmin in log)
    # One pooled row per predicted match; probabilities are a valid distribution.
    assert {"pH", "pD", "pA", "comp_class"} <= set(pooled.columns)
    assert np.allclose(pooled[["pH", "pD", "pA"]].sum(axis=1), 1.0)
    # Pooled rows == union of the scored blocks (2006..2015 here), each year once.
    assert pooled["year"].min() >= 2006 and pooled["year"].max() <= 2015
    assert len(pooled) == sum(len(b) for _, _, b in
                              datasets.walk_forward_blocks(df, range(2006, 2016), min_train=50))


def test_block_rps_by_class_accounting():
    df = _multi_year()
    pooled = walk_forward_block_predictions(df, lambda: _Recorder([]), range(2006, 2016), min_train=50)
    res = block_rps_by_class(pooled)
    assert res["all"]["n"] == len(pooled)
    # The tier counts present partition the pooled rows.
    tier_n = sum(res[t]["n"] for t in ("competitive", "friendly", "other") if t in res)
    assert tier_n == len(pooled)
    assert "competitive" in res and 0.0 <= res["competitive"]["rps"] <= 1.0


def test_block_rps_by_class_perfect_and_worst():
    """RPS is 0 for a perfectly confident correct forecast and 1 for the confidently wrong one."""
    pooled = pd.DataFrame({
        "result": ["H", "A"], "comp_class": ["competitive", "competitive"],
        "pH": [1.0, 1.0], "pD": [0.0, 0.0], "pA": [0.0, 0.0],
    })
    res = block_rps_by_class(pooled)
    # match 1: confident-correct -> 0 ; match 2: confident-wrong (said H, was A) -> 1
    assert res["competitive"]["rps"] == pytest.approx(0.5)


# --------------------------------------------------------------------------- #
# Integration — the real Dixon-Coles model plugs into the harness
# --------------------------------------------------------------------------- #
def test_dixon_coles_runs_through_the_block_harness():
    df = _multi_year(per_year=120)
    pooled = walk_forward_block_predictions(
        df, lambda: DixonColesModel(half_life_days=547.0, max_goals=6), range(2008, 2016), min_train=200)
    assert np.allclose(pooled[["pH", "pD", "pA"]].sum(axis=1), 1.0)
    res = block_rps_by_class(pooled)
    assert "competitive" in res and res["competitive"]["n"] > 0
    assert 0.0 < res["competitive"]["rps"] < 1.0
