"""Tests for live grading (wcpred.live_grading). Synthetic data + tmp files, no network.

Covers the as-of future-masking (the leakage-critical core), the played-match filter, the frozen
prediction parser, reading H/D/A off a model + scoring it, and the report rendering.
Run: `pytest -q`
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import forecast, live_grading  # noqa: E402


def _matches() -> pd.DataFrame:
    """A small frame: some pre-WC games + WC-2026 group & knockout matches across two matchdays."""
    rows = [
        ("2026-05-01", "A", "B", 1, 0, "Friendly", 2026),
        ("2026-06-12", "A", "C", 2, 1, "FIFA World Cup", 2026),      # WC matchday 1
        ("2026-06-12", "B", "D", 0, 0, "FIFA World Cup", 2026),      # WC matchday 1
        ("2026-06-16", "A", "B", 3, 1, "FIFA World Cup", 2026),      # WC matchday 2
        ("2026-07-04", "A", "D", 2, 0, "FIFA World Cup", 2026),      # WC knockout
    ]
    df = pd.DataFrame(rows, columns=["date", "home_team", "away_team", "home_score",
                                     "away_score", "tournament", "year"])
    df["date"] = pd.to_datetime(df["date"])
    df["neutral"] = True
    df["played"] = df["home_score"].notna() & df["away_score"].notna()
    df["margin"] = df["home_score"] - df["away_score"]
    df["total_goals"] = df["home_score"] + df["away_score"]
    df["result"] = np.where(df["margin"] > 0, "H", np.where(df["margin"] < 0, "A", "D"))
    return df


# --------------------------------------------------------------------------- #
# mask_future_scores — the as-of core
# --------------------------------------------------------------------------- #
def test_mask_blanks_future_keeps_past():
    m = _matches()
    cutoff = pd.Timestamp("2026-06-16")
    masked = live_grading.mask_future_scores(m, cutoff)
    fut = masked[masked["date"] >= cutoff]
    assert (~fut["played"]).all()
    assert fut["home_score"].isna().all() and fut["away_score"].isna().all()
    assert fut["result"].isna().all()
    past = masked[masked["date"] < cutoff]
    assert past["played"].all()
    # past scores unchanged vs original
    orig_past = m[m["date"] < cutoff]
    assert (past["home_score"].to_numpy() == orig_past["home_score"].to_numpy()).all()


def test_mask_is_as_of_future_invariant():
    """The masked frame must not depend on any score dated on/after the cutoff — so a model built
    on it (and its prediction for a cutoff-day match) cannot see that match's result or any later."""
    m1 = _matches()
    m2 = m1.copy()
    cutoff = pd.Timestamp("2026-06-16")
    # Perturb only on/after the cutoff (different "future" results).
    fut = m2["date"] >= cutoff
    m2.loc[fut, "home_score"] = m2.loc[fut, "home_score"] + 5
    m2.loc[fut, "away_score"] = 0
    a = live_grading.mask_future_scores(m1, cutoff).reset_index(drop=True)
    b = live_grading.mask_future_scores(m2, cutoff).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)                  # identical regardless of future scores


# --------------------------------------------------------------------------- #
# played_wc_matches
# --------------------------------------------------------------------------- #
def test_played_wc_matches_filters_and_sorts():
    m = _matches()
    wc = live_grading.played_wc_matches(m)
    assert (wc["tournament"] == "FIFA World Cup").all() and (wc["year"] == 2026).all()
    assert wc["played"].all() and len(wc) == 4          # excludes the friendly
    assert wc["date"].is_monotonic_increasing


# --------------------------------------------------------------------------- #
# frozen predictions + scoring
# --------------------------------------------------------------------------- #
def test_frozen_group_predictions(tmp_path):
    p = tmp_path / "pre.json"
    p.write_text(json.dumps({"fixtures": [
        {"home": "Mexico", "away": "South Africa", "p_home": 0.73, "p_draw": 0.16, "p_away": 0.11},
    ]}), encoding="utf-8")
    fz = live_grading.frozen_group_predictions(p)
    assert fz[("Mexico", "South Africa")] == (0.73, 0.16, 0.11)
    assert live_grading.frozen_group_predictions(tmp_path / "missing.json") == {}


def test_prediction_hda_and_rps():
    M = forecast.reweight_to_outcome(np.ones((6, 6)) / 36.0, (0.5, 0.3, 0.2))
    model = forecast.ForecastMatchModel({("A", "B"): M}, {})
    p = live_grading.prediction_hda(model, "A", "B")
    assert p == pytest.approx((0.5, 0.3, 0.2), abs=2e-3)
    assert live_grading.prediction_hda(model, "X", "Y") is None
    # RPS: confident-correct -> 0 ; confident-wrong (predict away, actual home) -> 1 ; None -> None
    assert live_grading.rps_hda((1.0, 0.0, 0.0), "H") == pytest.approx(0.0)
    assert live_grading.rps_hda((0.0, 0.0, 1.0), "H") == pytest.approx(1.0)
    assert live_grading.rps_hda(None, "H") is None


# --------------------------------------------------------------------------- #
# summarize / render
# --------------------------------------------------------------------------- #
def _records() -> list[dict]:
    return [
        {"date": "2026-06-12", "stage": "group", "home": "A", "away": "C", "score": "2-1",
         "result": "H", "rps_frozen": 0.10, "rps_off": 0.12, "rps_on": 0.12},
        {"date": "2026-07-04", "stage": "KO", "home": "A", "away": "D", "score": "2-0",
         "result": "H", "rps_frozen": None, "rps_off": 0.20, "rps_on": 0.16},
    ]


def test_summarize_all_vs_group_and_lead():
    s = live_grading.summarize(_records())
    assert s["n"] == 2 and s["n_group"] == 1
    assert s["all_off"] == pytest.approx(0.16) and s["all_on"] == pytest.approx(0.14)
    assert s["group_frozen"] == pytest.approx(0.10)      # frozen only on the group match
    assert s["lead"] == "xG-adjusted" and s["margin"] == pytest.approx(0.02)


def test_render_empty_and_populated():
    empty = live_grading.render_report([], "2026-06-07", "2026-06-14")
    assert "Awaiting matches" in empty
    rep = live_grading.render_report(_records(), "2026-07-04", "2026-07-05")
    assert "Running RPS" in rep and "xG-adjusted" in rep
    assert "A v C" in rep and "A v D" in rep              # per-match rows
    assert "0.1600" in rep and "0.1400" in rep            # all-match running RPS off/on
