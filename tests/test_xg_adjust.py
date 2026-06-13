"""Tests for the in-tournament xG adjustment (wcpred.xg_adjust). Synthetic data, no network.

Covers the effective-scoreline maths, the frame transform (only played target rows rewritten,
derived columns recomputed), the live-stats loader, and — the leakage-critical property — that the
adjustment is strictly as-of: a match's pre-match Elo is invariant to adjusting that match's own
scoreline or any LATER match, so no future information can reach its prediction.
Run: `pytest -q`
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import elo, xg_adjust  # noqa: E402


# --------------------------------------------------------------------------- #
# effective_scoreline
# --------------------------------------------------------------------------- #
def test_effective_scoreline_off_paths_return_raw():
    assert xg_adjust.effective_scoreline(1, 0, 2.4, 0.3, lam=0.5, shrink=0.0) == (1, 0)   # shrink 0
    assert xg_adjust.effective_scoreline(1, 0, 2.4, 0.3, lam=1.0, shrink=1.0) == (1, 0)   # lam 1


def test_effective_scoreline_pure_xg_and_blend():
    # lam=0, shrink=1 -> round(xg): a 0-1 result with xG 1.8-0.4 becomes a 2-0 "performance".
    assert xg_adjust.effective_scoreline(0, 1, 1.8, 0.4, lam=0.0, shrink=1.0) == (2, 0)
    # balanced half-blend nudges toward xG but stays close to the result.
    eh, ea = xg_adjust.effective_scoreline(0, 1, 1.8, 0.9, lam=0.5, shrink=0.75)
    assert (eh, ea) == (1, 1)               # 0 + .375*1.8 = .675->1 ; 1 + .375*(-.1)=.96->1
    assert eh >= 0 and ea >= 0


# --------------------------------------------------------------------------- #
# Synthetic history
# --------------------------------------------------------------------------- #
def _history() -> tuple[pd.DataFrame, pd.DataFrame]:
    """A short pre-WC history + a 6-match WC among 4 teams, plus per-match xG for the WC."""
    teams = ["A", "B", "C", "D"]
    rows, xg_rows = [], []
    d = pd.Timestamp("2017-06-01")
    # pre-tournament friendlies (no xG, never adjusted)
    for i in range(12):
        d += pd.Timedelta(days=10)
        h, a = teams[i % 4], teams[(i + 1) % 4]
        rows.append((d, h, a, 1, 1, "Friendly", 2018))
    # the World Cup: every ordered-ish pair, with xG that diverges from goals
    wc_start = pd.Timestamp("2018-06-14")
    pairs = [("A", "B", 0, 1, 1.9, 0.5), ("C", "D", 2, 2, 1.1, 2.4),
             ("A", "C", 1, 0, 0.6, 1.8), ("B", "D", 3, 0, 2.7, 0.4),
             ("A", "D", 0, 0, 1.5, 0.7), ("B", "C", 1, 1, 0.8, 1.3)]
    for i, (h, a, hg, ag, hxg, axg) in enumerate(pairs):
        dt = wc_start + pd.Timedelta(days=i)
        rows.append((dt, h, a, hg, ag, "FIFA World Cup", 2018))
        xg_rows.append((dt, h, a, hg, ag, hxg, axg))
    m = pd.DataFrame(rows, columns=["date", "home_team", "away_team", "home_score",
                                    "away_score", "tournament", "year"])
    m["neutral"] = True
    m["played"] = True
    m["margin"] = m["home_score"] - m["away_score"]
    m["total_goals"] = m["home_score"] + m["away_score"]
    m["result"] = np.where(m["margin"] > 0, "H", np.where(m["margin"] < 0, "A", "D"))
    xg = pd.DataFrame(xg_rows, columns=["date", "home_team", "away_team", "home_goals",
                                        "away_goals", "home_xg", "away_xg"])
    return m, xg


# --------------------------------------------------------------------------- #
# apply_effective_scores
# --------------------------------------------------------------------------- #
def test_apply_only_rewrites_target_played_rows_and_recomputes():
    m, xg = _history()
    out, n = xg_adjust.apply_effective_scores(m, xg, lam=0.0, shrink=1.0, years=(2018,))
    assert n == 6                                           # the 6 WC matches
    # friendlies (no xG) are untouched
    fr = out[out["tournament"] == "Friendly"]
    assert (fr["home_score"] == 1).all() and (fr["away_score"] == 1).all()
    # WC rows are rewritten to round(xg) and derived columns are consistent
    wc = out[out["tournament"] == "FIFA World Cup"]
    assert (wc["margin"] == wc["home_score"] - wc["away_score"]).all()
    assert (wc["total_goals"] == wc["home_score"] + wc["away_score"]).all()
    exp = np.where(wc["margin"] > 0, "H", np.where(wc["margin"] < 0, "A", "D"))
    assert (wc["result"].to_numpy() == exp).all()
    # A 0-1 with xG 1.9-0.5 (pure xG) flips to a home performance win.
    ab = wc[(wc["home_team"] == "A") & (wc["away_team"] == "B")].iloc[0]
    assert (ab["home_score"], ab["away_score"]) == (2, 1) or ab["result"] == "H"


def test_apply_is_noop_when_off_or_no_xg():
    m, xg = _history()
    out0, n0 = xg_adjust.apply_effective_scores(m, xg, lam=0.5, shrink=0.0, years=(2018,))
    assert n0 == 0 and out0 is m                            # shrink 0 -> untouched original
    out1, n1 = xg_adjust.apply_effective_scores(m, None, lam=0.5, shrink=0.75)
    assert n1 == 0 and out1 is m


def test_apply_respects_year_filter():
    m, xg = _history()
    _, n = xg_adjust.apply_effective_scores(m, xg, lam=0.0, shrink=1.0, years=(2022,))
    assert n == 0                                           # no 2022 WC rows in this history


# --------------------------------------------------------------------------- #
# Live-stats loader
# --------------------------------------------------------------------------- #
def test_load_match_stats_template_is_none(tmp_path):
    p = tmp_path / "stats.csv"
    p.write_text("date,home_team,away_team,home_goals,away_goals,home_xg,away_xg\n", encoding="utf-8")
    assert xg_adjust.load_match_stats(p) is None           # header-only template -> no usable rows
    assert xg_adjust.load_match_stats(tmp_path / "missing.csv") is None


def test_load_match_stats_requires_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("date,home_team,away_team\n2026-06-12,A,B\n", encoding="utf-8")
    with pytest.raises(ValueError):
        xg_adjust.load_match_stats(p)


# --------------------------------------------------------------------------- #
# LEAKAGE-CRITICAL: the adjustment is strictly as-of
# --------------------------------------------------------------------------- #
def _prematch_elo(frame: pd.DataFrame) -> dict:
    """{(date, home, away) -> (elo_home, elo_away)} pre-match, from a compute_elo run."""
    e, _ = elo.compute_elo(frame)
    out = {}
    for r in e.itertuples(index=False):
        out[(pd.Timestamp(r.date).date().isoformat(), r.home_team, r.away_team)] = (r.elo_home, r.elo_away)
    return out


def test_adjustment_is_as_of_no_future_leakage():
    """A WC match's PRE-match Elo must be invariant to adjusting that match itself or any LATER one.

    Adjust the whole tournament, then for each WC match rebuild a frame in which only the STRICTLY
    EARLIER WC matches are adjusted; the match's pre-match Elo must be identical. This proves no
    future (or own-match) scoreline leaks into the rating going into its prediction.
    """
    m, xg = _history()
    full = xg_adjust.apply_effective_scores(m, xg, lam=0.0, shrink=1.0, years=(2018,))[0]
    pm_full = _prematch_elo(full)

    wc = m[m["tournament"] == "FIFA World Cup"].sort_values("date")
    for r in wc.itertuples(index=False):
        key = (pd.Timestamp(r.date).date().isoformat(), r.home_team, r.away_team)
        xg_before = xg[xg["date"] < r.date]                # adjust only strictly-earlier WC matches
        partial = xg_adjust.apply_effective_scores(m, xg_before, lam=0.0, shrink=1.0, years=(2018,))[0]
        pm_partial = _prematch_elo(partial)
        assert pm_partial[key] == pytest.approx(pm_full[key]), f"future leakage into {key}"
