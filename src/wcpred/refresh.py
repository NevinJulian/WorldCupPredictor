"""Helpers for the matchday refresh loop (scripts/10_refresh.py).

Small, importable, side-effect-light pieces the one-command refresh and the metadata stampers
share: how many matches are played (overall + this tournament), and the one-time snapshot of the
pre-tournament forecast to an immutable record. Kept here (not in the numbered script, which is not
importable) so they can be unit-tested.

The refresh itself is a pure re-run of the existing as-of chain — no model change — so it is
leakage-safe by construction: only played matches ever inform later-match predictions.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from . import ROOT

# The 2026 finals carry this exact tournament label in the data (qualifiers are a different label).
WC_2026_TOURNAMENT = "FIFA World Cup"
WC_2026_YEAR = 2026

# Immutable pre-tournament record (snapshotted once on the first refresh, never overwritten).
PRETOURNAMENT_JSON = ROOT / "data" / "processed" / "forecast_2026_pretournament.json"
PRETOURNAMENT_MD = ROOT / "reports" / "forecast_2026_pretournament.md"
LIVE_JSON = ROOT / "data" / "processed" / "forecast_2026.json"
LIVE_MD = ROOT / "reports" / "forecast_2026.md"

_PRETOURNAMENT_BANNER = (
    "> **Immutable pre-tournament record.** Snapshot of the v0.4.0 forecast taken before the "
    "first matchday refresh — preserved for later grading. Do not edit; the live forecast lives "
    "in `forecast_2026.md`.\n\n"
)


def total_played_count(matches: pd.DataFrame) -> int:
    """Number of played matches in the data (a data-freshness counter)."""
    return int(matches["played"].astype(bool).sum())


def wc2026_played_count(matches: pd.DataFrame) -> int:
    """Number of WC-2026 finals matches already played (the in-tournament progress counter).

    Filters to the 2026 ``FIFA World Cup`` finals label (not qualifiers, not historical World
    Cups) and counts the played rows. 0 before kickoff; rises as martj42 fills in scores.
    """
    t = matches["tournament"].astype(str)
    mask = (t == WC_2026_TOURNAMENT) & (matches["year"] == WC_2026_YEAR) & matches["played"].astype(bool)
    return int(mask.sum())


def played_counts(matches: pd.DataFrame) -> dict[str, int]:
    """Both counters as a metadata dict: ``{"matches_played", "wc2026_matches_played"}``."""
    return {"matches_played": total_played_count(matches),
            "wc2026_matches_played": wc2026_played_count(matches)}


def snapshot_pretournament(
    live_json: Path = LIVE_JSON, live_md: Path = LIVE_MD,
    pre_json: Path = PRETOURNAMENT_JSON, pre_md: Path = PRETOURNAMENT_MD,
) -> bool:
    """Snapshot the current forecast to the immutable pre-tournament record, once.

    Copies the live ``forecast_2026.{json,md}`` to ``forecast_2026_pretournament.{json,md}`` only
    if the snapshot does not already exist — so it is created on the first refresh and never
    overwritten thereafter, preserving the pristine pre-tournament prediction. The Markdown copy
    gets a short immutability banner; the JSON is copied verbatim (the machine record). Returns
    True if it created the snapshot, False if it already existed (or there was nothing to copy).
    """
    if pre_json.exists():
        return False
    if not live_json.exists():
        return False
    pre_json.parent.mkdir(parents=True, exist_ok=True)
    pre_md.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(live_json, pre_json)
    if live_md.exists():
        pre_md.write_text(_PRETOURNAMENT_BANNER + live_md.read_text(encoding="utf-8"), encoding="utf-8")
    return True
