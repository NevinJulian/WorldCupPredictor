"""Live grading of the WC-2026 forecast — a running A/B on the real tournament.

After each matchday refresh we score the prediction made BEFORE each now-played WC match, for
three variants on the same fixtures:

  1. **frozen pre-tournament** — the immutable `forecast_2026_pretournament.json` (group fixtures
     only; knockout pairings didn't exist before the draw resolved),
  2. **live result-only** — the model rebuilt as-of with the xG adjustment OFF,
  3. **live xG-adjusted** — the model rebuilt as-of with the xG adjustment ON.

This turns the unprovable 2-WC xG backtest (reports/xg_adjust_gate.md) into a live A/B: as games
accumulate we can see whether the xG-adjusted forecast actually beats result-only on THIS
tournament, and flip `xg_adjust.XG_ADJUST_DEFAULT` on real evidence.

**As-of / leakage-free.** A match is graded only after it is played, and each live variant's
prediction is built from data strictly before that match's matchday — `mask_future_scores` blanks
every score on or after the cutoff, so the match (and everything later) is an *unplayed fixture*
when the model that predicts it is fit. A match never informs its own (or an earlier match's)
prediction.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics

WC_TOURNAMENT = "FIFA World Cup"
WC_YEAR = 2026


def played_wc_matches(matches: pd.DataFrame) -> pd.DataFrame:
    """The played WC-2026 finals matches (group + knockout), sorted by date."""
    m = matches[(matches["tournament"].astype(str) == WC_TOURNAMENT)
                & (matches["year"] == WC_YEAR) & matches["played"].astype(bool)]
    return m.sort_values("date", kind="stable")


def mask_future_scores(matches: pd.DataFrame, cutoff: "str | pd.Timestamp") -> pd.DataFrame:
    """Return a copy of `matches` with every score on/after `cutoff` blanked to unplayed.

    Rows dated ``>= cutoff`` have their goals set to NaN and ``played``/``result``/``margin``/
    ``total_goals`` recomputed accordingly (so the match becomes an unplayed *fixture*); rows
    before the cutoff are untouched. This is the as-of core: a model fit on the masked frame has
    seen only matches strictly before the cutoff, so its prediction for a cutoff-day match cannot
    depend on that match's result (or any later one).
    """
    cutoff = pd.Timestamp(cutoff)
    df = matches.copy()
    future = df["date"] >= cutoff
    df.loc[future, ["home_score", "away_score"]] = np.nan
    df["played"] = df["home_score"].notna() & df["away_score"].notna()
    df["margin"] = df["home_score"] - df["away_score"]
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["result"] = np.where(df["margin"] > 0, "H", np.where(df["margin"] < 0, "A", "D"))
    df.loc[~df["played"], "result"] = np.nan
    return df


def frozen_group_predictions(pretournament_path: "str | Path") -> dict[tuple[str, str], tuple[float, float, float]]:
    """{(home_display, away_display) -> (p_home, p_draw, p_away)} from the frozen pre-tournament JSON.

    Covers the 72 group fixtures only (display-name keyed, matching the forecast output). Returns
    an empty dict if the snapshot is missing.
    """
    path = Path(pretournament_path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(fx["home"], fx["away"]): (fx["p_home"], fx["p_draw"], fx["p_away"])
            for fx in data.get("fixtures", [])}


def prediction_hda(model, home: str, away: str) -> "tuple[float, float, float] | None":
    """(p_home, p_draw, p_away) for a fixture from a built ForecastMatchModel, or None if absent."""
    if (home, away) not in model.matrices:
        return None
    M = model.matrices[(home, away)]
    return (float(np.tril(M, -1).sum()), float(np.trace(M)), float(np.triu(M, 1).sum()))


def rps_hda(p: "tuple[float, float, float] | None", actual_result: str) -> "float | None":
    """Normalized RPS of an H/D/A forecast against the realized 'H'/'D'/'A' result (None -> None)."""
    if p is None:
        return None
    return metrics.rps([list(p)], [actual_result])


# --------------------------------------------------------------------------- #
# Report rendering
# --------------------------------------------------------------------------- #
def _mean(values: list) -> "float | None":
    vals = [v for v in values if v is not None]
    return float(np.mean(vals)) if vals else None


def summarize(records: list[dict]) -> dict:
    """Running RPS per variant. `frozen`/`group_*` are over the common group fixtures (where the
    frozen prediction exists); `all_*` are over every graded match (the result-only vs xG A/B)."""
    group = [r for r in records if r["rps_frozen"] is not None]
    off_all = _mean([r["rps_off"] for r in records])
    on_all = _mean([r["rps_on"] for r in records])
    return {
        "n": len(records), "n_group": len(group),
        "all_off": off_all, "all_on": on_all,
        "group_frozen": _mean([r["rps_frozen"] for r in group]),
        "group_off": _mean([r["rps_off"] for r in group]),
        "group_on": _mean([r["rps_on"] for r in group]),
        "lead": (None if off_all is None or on_all is None
                 else ("xG-adjusted" if on_all < off_all else
                       "result-only" if off_all < on_all else "tied")),
        "margin": (None if off_all is None or on_all is None else abs(off_all - on_all)),
    }


def _fmt(x: "float | None", pct: bool = False) -> str:
    if x is None:
        return "—"
    return f"{x*100:.0f}%" if pct else f"{x:.4f}"


def render_report(records: list[dict], as_of: str, generated: str) -> str:
    """Render reports/live_grading.md from the per-match grade records."""
    s = summarize(records)
    L = [
        "# WC 2026 — live forecast grading (A/B)",
        "",
        f"*Generated {generated}; data as-of {as_of}. Running RPS (lower is better) of the "
        f"**pre-match** prediction for every played WC-2026 match, for three variants on the same "
        f"fixtures. As-of / leakage-free: each live prediction is built from data strictly before "
        f"the match's matchday. Frozen = the immutable pre-tournament forecast (group fixtures "
        f"only). The headline is the live **result-only vs xG-adjusted** A/B.*",
        "",
    ]
    if not records:
        L += ["## Awaiting matches",
              "",
              "No WC-2026 matches have been played yet (or none are in the data). This report "
              "populates automatically as the matchday refresh ingests results.", ""]
        return "\n".join(L)

    lead = s["lead"]
    headline = ("tied so far" if lead == "tied"
                else f"**{lead}** leads by {s['margin']:.4f} RPS")
    L += [
        "## Running RPS",
        "",
        f"Headline A/B over all {s['n']} graded matches: result-only **{_fmt(s['all_off'])}** vs "
        f"xG-adjusted **{_fmt(s['all_on'])}** → {headline}.",
        "",
        "| Variant | RPS (all matches) | RPS (group fixtures) | n |",
        "|--|--:|--:|--:|",
        f"| Frozen pre-tournament | — | {_fmt(s['group_frozen'])} | {s['n_group']} |",
        f"| Live result-only (xG off) | {_fmt(s['all_off'])} | {_fmt(s['group_off'])} | {s['n']} |",
        f"| Live xG-adjusted (xG on) | {_fmt(s['all_on'])} | {_fmt(s['group_on'])} | {s['n']} |",
        "",
        "*The group-fixtures column is the clean three-way comparison on identical fixtures; the "
        "all-matches column adds knockout games (frozen has no knockout prediction).*",
        "",
        "## Per-match",
        "",
        "| Date | Stage | Match | Score | Result | Frozen | Result-only | xG-adj |",
        "|--|--|--|:--:|:--:|--:|--:|--:|",
    ]
    for r in records:
        L.append(f"| {r['date']} | {r['stage']} | {r['home']} v {r['away']} | {r['score']} | "
                 f"{r['result']} | {_fmt(r['rps_frozen'])} | {_fmt(r['rps_off'])} | {_fmt(r['rps_on'])} |")
    L += ["",
          f"*{s['n']} matches graded ({s['n_group']} group). Early on the sample is small and "
          "result-only ≈ xG-adjusted (few prior games to re-weight); the gap is meaningful only as "
          "games accumulate.*", ""]
    return "\n".join(L)
