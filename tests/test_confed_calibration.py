"""Unit tests for ConfederationCalibrator. Synthetic data, no network. Run: `pytest -q`

The load-bearing guard is **leakage**: a per-WC fold's offsets are estimated from that fold's
pre-tournament training set only — injecting wildly biased matches dated on/after the test WC
must not change the fold's offsets (they are excluded by the time split). Also checks the tilt
direction, draw-mass preservation, passthrough, and the residual sign.
"""
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import datasets, models  # noqa: E402


def _confed_frame(seed: int = 0) -> pd.DataFrame:
    """Synthetic feature-shaped frame: confederation-biased friendlies + a WC-2018 finals fold."""
    rng = np.random.default_rng(seed)
    confeds = ["UEFA", "CONMEBOL", "AFC", "CAF"]
    bias = {"UEFA": 0.15, "CONMEBOL": 0.10, "AFC": -0.15, "CAF": -0.10}   # win-prob nudge
    rows, date = [], pd.Timestamp("2000-01-01")
    for _ in range(700):
        date += pd.Timedelta(days=8)
        ch, ca = rng.choice(confeds, 2, replace=False)
        ediff = float(rng.normal(0, 120))
        p_home = 1.0 / (1.0 + 10 ** (-ediff / 400)) + bias[ch] - bias[ca]
        u = rng.random()
        res = "H" if u < p_home - 0.13 else ("A" if u > p_home + 0.13 else "D")
        rows.append({"date": date, "home_confed": ch, "away_confed": ca, "elo_diff": ediff,
                     "neutral": True, "result": res, "tournament": "Friendly", "played": True})
    wc = pd.Timestamp("2018-06-14")
    for _ in range(8):
        wc += pd.Timedelta(days=1)
        ch, ca = rng.choice(confeds, 2, replace=False)
        rows.append({"date": wc, "home_confed": ch, "away_confed": ca,
                     "elo_diff": float(rng.normal(0, 100)), "neutral": True,
                     "result": rng.choice(["H", "D", "A"]), "tournament": "FIFA World Cup",
                     "played": True})
    df = pd.DataFrame(rows)
    df["year"] = df["date"].dt.year
    return df


# --------------------------------------------------------------------------- #
# Tilt mechanics
# --------------------------------------------------------------------------- #
def test_adjust_tilts_toward_higher_offset_and_preserves_draw():
    cal = models.ConfederationCalibrator(sensitivity=4.0)
    cal.offsets_ = {"X": 0.10, "Y": -0.10}
    p = np.array([[0.40, 0.30, 0.30]])
    up = cal.adjust(p, ["X"], ["Y"])[0]        # home confed favoured
    assert up[0] > 0.40 and up[2] < 0.30
    assert up[1] == pytest.approx(0.30)        # draw mass preserved
    assert up.sum() == pytest.approx(1.0)
    down = cal.adjust(p, ["Y"], ["X"])[0]      # away confed favoured
    assert down[0] < 0.40 and down[2] > 0.30


def test_adjust_passthrough_when_no_offset():
    cal = models.ConfederationCalibrator()
    cal.offsets_ = {}
    p = np.array([[0.5, 0.2, 0.3], [0.1, 0.4, 0.5]])
    assert np.allclose(cal.adjust(p, ["X", "Z"], ["Y", "W"]), p)


def test_estimate_residual_sign():
    # X (home) wins every inter-confed game but the model only gave it 0.55 win-share -> +offset.
    df = pd.DataFrame({"home_confed": ["X"] * 12, "away_confed": ["Y"] * 12, "result": ["H"] * 12})
    proba = np.tile([0.4, 0.3, 0.3], (12, 1))
    cal = models.ConfederationCalibrator(shrinkage=0.0, min_matches=1)
    off = cal._estimate(df, proba)
    assert off["X"] > 0 and off["Y"] < 0
    assert off["X"] == pytest.approx(1.0 - 0.55)     # actual 1.0 - model win-share (0.4+0.5*0.3)


# --------------------------------------------------------------------------- #
# Leakage: a fold's offsets use no match dated on/after the test WC
# --------------------------------------------------------------------------- #
def test_fold_offsets_use_no_future_matches():
    feat = _confed_frame()
    train, _ = datasets.tournament_holdout(feat, 2018)
    off1 = models.ConfederationCalibrator(min_matches=5).fit(train).offsets_

    # Poison: extreme post-cutoff (2019) inter-confed games where AFC wins everything.
    poison = pd.DataFrame([{
        "date": pd.Timestamp("2019-03-01") + pd.Timedelta(days=d), "home_confed": "AFC",
        "away_confed": "UEFA", "elo_diff": 0.0, "neutral": True, "result": "H",
        "tournament": "Friendly", "played": True, "year": 2019} for d in range(60)])
    train2, _ = datasets.tournament_holdout(pd.concat([feat, poison], ignore_index=True), 2018)
    off2 = models.ConfederationCalibrator(min_matches=5).fit(train2).offsets_

    assert train2["date"].max() < pd.Timestamp("2018-01-01")   # fold-2018 train excludes 2019
    assert off1 == off2                                         # so the offsets are unchanged


def test_walk_forward_confed_calibrated_runs():
    feat = _confed_frame()
    rows = models.walk_forward_confed_calibrated(
        feat, years=(2018,), base_factory=models.EloLogisticModel, min_matches=5)
    assert len(rows) == 1
    r = rows[0]
    assert r["year"] == 2018 and r["n"] == 8
    assert 0.0 <= r["rps_base"] <= 1.0 and 0.0 <= r["rps_cal"] <= 1.0
    assert isinstance(r["offsets"], dict)
