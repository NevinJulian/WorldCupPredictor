"""In-tournament xG adjustment of team strength (gated; see reports/xg_adjust_gate.md).

In a 1-3 game in-tournament sample, **xG is a far less noisy performance signal than goals** —
goals fold in finishing variance (a team can dominate xG yet lose 0-1). So when a played World Cup
result enters the as-of history, we optionally replace its scoreline with an **xG-adjusted
effective scoreline** before it updates the ratings:

    g_eff = round( goals + shrink * (1 - lam) * (xG - goals) ),  clipped at 0

two knobs, both conservative by default:
  * ``lam``    — weight on the actual goals (``1 - lam`` is the xG trust). ``lam = 1`` -> raw.
  * ``shrink`` — how far the scoreline moves from the raw result toward that goal/xG blend.
                 ``shrink = 0`` -> raw scoreline (the adjustment is OFF). Small ``shrink`` keeps a
                 single game from moving a team much (the pre-tournament prior dominates).

Because the effective scoreline simply *replaces* the played scoreline at the top of the existing
chain (clean -> elo -> features -> Dixon-Coles -> snapshot), the adjustment propagates everywhere
consistently and is **as-of / leakage-free by construction**: it only rewrites matches that have
already been played, and every downstream rating update remains strictly sequential.

The lever is xG only. Optional shots / shots-on-target columns may ride along in the stats file but
are deliberately NOT weighted into the update (low marginal signal).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

WC_TOURNAMENT = "FIFA World Cup"
WC_2026_YEAR = 2026

# --- Shipped defaults (set by the gate, reports/xg_adjust_gate.md) ----------------------------- #
# The 2018+2022 in-tournament backtest shows the xG-adjusted update IMPROVING the pooled later-match
# RPS (best config -0.0035; most of the sweep <= 0), so it ships ON per the gate's improve-or-neutral
# rule. The improvement is not statistically significant (96 matches, 2 WCs — CI spans 0), so we ship
# a CONSERVATIVE BALANCED default (equal goal/xG trust, moderate strength: backtest delta -0.0015)
# rather than the aggressive pure-xG optimum. Revisit once 2026 provides more in-tournament xG.
XG_ADJUST_DEFAULT = True      # whether build_forecast_model applies it by default
XG_LAMBDA = 0.5               # weight on actual goals; (1 - lam) = xG trust
XG_SHRINK = 0.75              # conservatism: 0 = off, 1 = full goal/xG blend

# Required + optional columns of a match-stats file (live or historical).
REQUIRED_STAT_COLS = ("date", "home_team", "away_team", "home_goals", "away_goals", "home_xg", "away_xg")
OPTIONAL_STAT_COLS = ("home_shots", "away_shots", "home_sot", "away_sot")   # carried, never weighted


def _round_nonneg(value: float) -> int:
    """Round half-up to the nearest non-negative integer (values are convex combos of g, xG >= 0)."""
    return int(max(0.0, np.floor(value + 0.5)))


def effective_scoreline(gh: float, ga: float, xgh: float, xga: float,
                        lam: float = XG_LAMBDA, shrink: float = XG_SHRINK) -> tuple[int, int]:
    """xG-adjusted ``(home, away)`` goals: ``round(g + shrink*(1-lam)*(xG - g))``, clipped >= 0.

    ``shrink = 0`` or ``lam = 1`` returns the raw scoreline. The result is a non-negative integer
    pair, so it drops straight into the Elo update and the Dixon-Coles Poisson likelihood.
    """
    c = shrink * (1.0 - lam)
    return _round_nonneg(gh + c * (xgh - gh)), _round_nonneg(ga + c * (xga - ga))


def _xg_lookup(xg: pd.DataFrame) -> dict[tuple[str, str, str], tuple[float, float]]:
    """{(date_str, home_team, away_team) -> (home_xg, away_xg)} for fast row matching."""
    out: dict[tuple[str, str, str], tuple[float, float]] = {}
    for r in xg.itertuples(index=False):
        d = pd.Timestamp(r.date).date().isoformat()
        out[(d, r.home_team, r.away_team)] = (float(r.home_xg), float(r.away_xg))
    return out


def apply_effective_scores(
    matches: pd.DataFrame, xg: pd.DataFrame | None,
    lam: float = XG_LAMBDA, shrink: float = XG_SHRINK,
    *, years: "tuple[int, ...] | list[int] | None" = None, tournament: str = WC_TOURNAMENT,
) -> tuple[pd.DataFrame, int]:
    """Replace played ``tournament`` finals scorelines with their xG-effective values.

    ``xg`` carries per-match ``home_xg``/``away_xg`` (matched by date + team names). Only played
    rows of ``tournament`` (optionally restricted to ``years``) that have a matching xG entry are
    rewritten; ``result`` / ``margin`` / ``total_goals`` are recomputed for them. Everything else
    is untouched. With ``shrink <= 0`` (the off default) or no xG, returns ``matches`` unchanged.

    Returns ``(adjusted_matches, n_adjusted)``. As-of safe: it only rewrites already-played rows,
    so no future information is introduced — downstream Elo/feature updates stay sequential.
    """
    if xg is None or len(xg) == 0 or shrink <= 0.0 or lam >= 1.0:
        return matches, 0

    lookup = _xg_lookup(xg)
    df = matches.copy()
    is_target = (df["tournament"].astype(str) == tournament) & df["played"].astype(bool)
    if years is not None:
        is_target &= df["year"].isin(list(years))

    changed = []
    hs = df["home_score"].to_numpy(dtype=float).copy()
    as_ = df["away_score"].to_numpy(dtype=float).copy()
    dates = df["date"].to_numpy()
    home = df["home_team"].to_numpy()
    away = df["away_team"].to_numpy()
    for i in np.flatnonzero(is_target.to_numpy()):
        key = (pd.Timestamp(dates[i]).date().isoformat(), home[i], away[i])
        if key not in lookup:
            continue
        xgh, xga = lookup[key]
        eh, ea = effective_scoreline(hs[i], as_[i], xgh, xga, lam, shrink)
        hs[i], as_[i] = eh, ea
        changed.append(i)

    if not changed:
        return matches, 0

    df["home_score"] = hs
    df["away_score"] = as_
    df["margin"] = df["home_score"] - df["away_score"]
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["result"] = np.where(df["margin"] > 0, "H", np.where(df["margin"] < 0, "A", "D"))
    df.loc[~df["played"].astype(bool), "result"] = np.nan
    return df, len(changed)


def load_match_stats(path: "str | Path") -> "pd.DataFrame | None":
    """Load a match-stats CSV (live WC-2026 file or the historical 2018/2022 file).

    Returns the frame (with ``date`` parsed) or ``None`` if the file is absent or has no usable
    rows. Requires ``REQUIRED_STAT_COLS``; optional shots columns are kept but never weighted.
    """
    path = Path(path)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_STAT_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} missing required columns: {missing}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_team", "away_team", "home_xg", "away_xg"])
    return df if len(df) else None


def adjust_matches_for_forecast(
    matches: pd.DataFrame, stats_path: "str | Path",
    lam: float = XG_LAMBDA, shrink: float = XG_SHRINK,
) -> tuple[pd.DataFrame, int]:
    """Apply the live WC-2026 xG adjustment for the forecast, if a stats file is present.

    Reads the WC-2026 match-stats CSV and rewrites the played 2026 finals scorelines to their
    xG-effective values. No file (or no played WC games yet) -> ``matches`` unchanged.
    """
    stats = load_match_stats(stats_path)
    if stats is None:
        return matches, 0
    return apply_effective_scores(matches, stats, lam, shrink, years=(WC_2026_YEAR,))
