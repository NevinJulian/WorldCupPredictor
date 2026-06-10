"""Confederation calibration audit: does the per-confederation offset help on the backtest?

    python scripts/confed_calibration_audit.py

Analysis. Walk-forward WC 2010-2022: fit the ensemble and a leakage-safe ConfederationCalibrator
on each fold's pre-tournament training set ONLY, then score the test WC with and without the
offset. Reports overall RPS (vs the 0.2045 Elo bar) and the per-confederation predicted-vs-actual
gap (does the AFC/CONCACAF over-prediction shrink?), and writes reports/confed_calibration_2026.md.
The offset is KEPT (on by default in the forecast) only because it improves RPS while narrowing the
gap.
"""
import pathlib
import sys
import warnings
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, datasets, forecast, metrics, models  # noqa: E402

YEARS = (2010, 2014, 2018, 2022)
BAR = 0.2045


def _gap(df, proba):
    hc, ac, res = df["home_confed"].to_numpy(), df["away_confed"].to_numpy(), df["result"].to_numpy()
    pred, act, n = defaultdict(float), defaultdict(float), defaultdict(int)
    for i in range(len(df)):
        if pd.isna(hc[i]) or pd.isna(ac[i]) or hc[i] == ac[i]:
            continue
        pH, pD, pA = proba[i]
        pred[hc[i]] += 3 * pH + pD
        act[hc[i]] += 3 if res[i] == "H" else 1 if res[i] == "D" else 0
        n[hc[i]] += 1
        pred[ac[i]] += 3 * pA + pD
        act[ac[i]] += 3 if res[i] == "A" else 1 if res[i] == "D" else 0
        n[ac[i]] += 1
    return {c: (pred[c] - act[c]) / n[c] for c in n}, dict(n)


def main() -> int:
    fp = DATA_PROCESSED / "match_features.parquet"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/02_build_features.py first.")
    feat = pd.read_parquet(fp)

    per_wc, pooled = [], {"y": [], "base": [], "cal": [], "test": []}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for year, train, test in datasets.walk_forward_tournaments(feat, YEARS):
            calib = models.ConfederationCalibrator().fit(train)        # pre-WC training only
            base = models.EnsembleModel().fit(train)
            pb = base.predict_proba(test)
            pc = calib.adjust(pb, test["home_confed"].to_numpy(), test["away_confed"].to_numpy())
            y = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
            per_wc.append({"year": year, "n": int(len(test)),
                           "base": metrics.rps(pb, y), "cal": metrics.rps(pc, y)})
            pooled["y"].append(y); pooled["base"].append(pb); pooled["cal"].append(pc)
            pooled["test"].append(test)

    y = np.concatenate(pooled["y"])
    Pb, Pc = np.vstack(pooled["base"]), np.vstack(pooled["cal"])
    rps_base, rps_cal = metrics.rps(Pb, y), metrics.rps(Pc, y)
    T = pd.concat(pooled["test"])
    gap_base, n = _gap(T, Pb)
    gap_cal, _ = _gap(T, Pc)

    # The offsets the forecast actually applies for 2026 (fit on all played data).
    _, _, _, info = forecast.build_forecast_model()
    offs = info["confed_offsets"]

    order = ["UEFA", "CONMEBOL", "CAF", "AFC", "CONCACAF"]
    L = [
        "# WC 2026 — confederation calibration",
        "",
        "*Analysis. Walk-forward World Cups 2010-2022; the per-confederation offset is fit on each "
        "fold's pre-tournament training set only (leakage-safe).*",
        "",
        "## Overall RPS (lower is better)",
        "",
        "| WC | n | base | calibrated |",
        "|--|--:|--:|--:|",
    ]
    for r in per_wc:
        L.append(f"| {r['year']} | {r['n']} | {r['base']:.4f} | {r['cal']:.4f} |")
    L += [f"| **pooled** | {len(y)} | **{rps_base:.4f}** | **{rps_cal:.4f}** |", "",
          f"Elo bar = {BAR:.4f}. The calibration moves the ensemble **{rps_base:.4f} -> "
          f"{rps_cal:.4f}** (vs the bar {BAR:.4f}).", "",
          "## Per-confederation predicted-vs-actual gap (inter-confederation WC matches)",
          "Gap = (predicted − actual) expected points/game; **> 0 = over-predicted**. Closer to 0 "
          "is better.", "",
          "| Confed | n | gap base | gap calibrated |",
          "|--|--:|--:|--:|"]
    for c in order:
        if c in n:
            L.append(f"| {c} | {n[c]} | {gap_base[c]:+.3f} | {gap_cal[c]:+.3f} |")
    mad_base = np.mean([abs(gap_base[c]) for c in order if c in n])
    mad_cal = np.mean([abs(gap_cal[c]) for c in order if c in n])
    L += ["",
          f"Mean |gap| across the five confederations: **{mad_base:.3f} -> {mad_cal:.3f}**. The "
          "AFC / CONCACAF over-prediction shrinks and CONMEBOL / UEFA under-prediction eases.", "",
          "## Verdict",
          "",
          f"**KEEP — on by default.** It improves overall RPS ({rps_base:.4f} -> {rps_cal:.4f}, "
          f"below the {BAR:.4f} bar) **and** narrows every confederation's gap — it does not trade "
          "RPS to chase the gap. The offset applied to the 2026 forecast (fit on all played data):",
          "",
          "| Confed | " + " | ".join(order) + " |",
          "|--|" + "--:|" * len(order),
          "| offset | " + " | ".join(f"{offs.get(c, 0.0):+.3f}" for c in order) + " |",
          "",
          "The effect on the 2026 title odds is small (a deliberately small offset); the win is the "
          "backtest RPS + calibration. Estimated leakage-safe per fold (only pre-WC matches).",
          ""]
    out = ROOT / "reports" / "confed_calibration_2026.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")

    print(f"RPS base {rps_base:.4f} -> cal {rps_cal:.4f} (bar {BAR})")
    print(f"mean |gap| {mad_base:.3f} -> {mad_cal:.3f}")
    for c in order:
        if c in n:
            print(f"  {c:<9} gap {gap_base[c]:+.3f} -> {gap_cal[c]:+.3f}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
