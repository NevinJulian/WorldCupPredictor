"""Tests for the matchday-refresh helpers (wcpred.refresh). Synthetic data + tmp files, no network.

Guards the two pieces the one-command refresh and the metadata stampers share: the played-match
counters (overall + this tournament) and the once-only, immutable pre-tournament snapshot.
Run: `pytest -q`
"""
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import refresh  # noqa: E402


def _matches() -> pd.DataFrame:
    """A tiny match frame mixing historical WC finals, WC-2026 fixtures (some played), and others."""
    return pd.DataFrame([
        # historical World Cup finals — must NOT count toward wc2026
        {"tournament": "FIFA World Cup", "year": 2022, "played": True},
        # WC-2026 finals: two played, one not
        {"tournament": "FIFA World Cup", "year": 2026, "played": True},
        {"tournament": "FIFA World Cup", "year": 2026, "played": True},
        {"tournament": "FIFA World Cup", "year": 2026, "played": False},
        # a 2026 WC qualifier — different label, must NOT count toward wc2026
        {"tournament": "FIFA World Cup qualification", "year": 2026, "played": True},
        # a friendly
        {"tournament": "Friendly", "year": 2026, "played": True},
    ])


def test_counts():
    m = _matches()
    assert refresh.wc2026_played_count(m) == 2          # only the 2 played 2026 finals
    assert refresh.total_played_count(m) == 5           # all but the one unplayed fixture
    assert refresh.played_counts(m) == {"matches_played": 5, "wc2026_matches_played": 2}


def test_wc2026_count_zero_before_kickoff():
    m = _matches()
    m["played"] = m["played"] & (m["tournament"] != "FIFA World Cup")   # no WC finals played yet
    assert refresh.wc2026_played_count(m) == 0


def test_snapshot_creates_once_and_is_immutable(tmp_path):
    live_json = tmp_path / "forecast_2026.json"
    live_md = tmp_path / "forecast_2026.md"
    pre_json = tmp_path / "forecast_2026_pretournament.json"
    pre_md = tmp_path / "forecast_2026_pretournament.md"
    live_json.write_text('{"v": 1}', encoding="utf-8")
    live_md.write_text("# pre-tournament forecast\n", encoding="utf-8")

    # First run: creates the snapshot (copies JSON verbatim, banners the MD).
    assert refresh.snapshot_pretournament(live_json, live_md, pre_json, pre_md) is True
    assert pre_json.read_text(encoding="utf-8") == '{"v": 1}'
    assert "Immutable pre-tournament record" in pre_md.read_text(encoding="utf-8")
    assert "# pre-tournament forecast" in pre_md.read_text(encoding="utf-8")

    # The live forecast then moves on...
    live_json.write_text('{"v": 2}', encoding="utf-8")
    # ...but a second snapshot is a no-op (never overwrites the immutable record).
    assert refresh.snapshot_pretournament(live_json, live_md, pre_json, pre_md) is False
    assert pre_json.read_text(encoding="utf-8") == '{"v": 1}'


def test_snapshot_noop_when_no_live_record(tmp_path):
    pre_json = tmp_path / "forecast_2026_pretournament.json"
    assert refresh.snapshot_pretournament(
        tmp_path / "missing.json", tmp_path / "missing.md", pre_json, tmp_path / "pre.md") is False
    assert not pre_json.exists()
