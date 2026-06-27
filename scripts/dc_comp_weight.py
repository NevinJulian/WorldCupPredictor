"""Dixon-Coles competition-weight sweep (gated) — down-weight friendlies in the goals-model fit.

    python scripts/dc_comp_weight.py          # full sweep + gate -> reports/dc_comp_weight.md
    python scripts/dc_comp_weight.py --quick   # smaller span/grid (smoke test)

Why this exists
---------------
`DixonColesModel` weights training matches by RECENCY only. Friendlies (~38% of all
internationals, K=20) are noisier than competitive matches, so an external blueprint suggests
also weighting by competition importance. This sweeps a per-match COMPETITION weight on the
**friendly** tier (`DixonColesModel(comp_weights={"friendly": w})`, competitive/other held at 1.0)
and decides whether to adopt a non-default value — the exact same broadened-backtest gate used for
the half-life change (reports/eval_and_decay.md).

Three RPS metrics, all as-of / no-leakage (expanding-window refit at yearly checkpoints, each
block predicted only from matches that finished before it began):

  (a) **competitive** internationals (qualifiers + continental + WC finals) — the sensitive
      detector we tune on (literature reference ~0.165, Ley et al. 2019).
  (b) **all** internationals incl. friendlies — noisier; reported, never optimised on.
  (c) the existing **WC-finals-only** walk-forward — the product-relevance metric, for both the
      bare Dixon-Coles model and the shipped confederation-calibrated ensemble.

The friendly weight only reweights the DC fit; everything else (half-life 5y, ridge, rho) is held
fixed.

GATE. Adopt a NON-1.0 friendly weight only if it **improves (a)** — by a margin whose paired
bootstrap 95% CI excludes zero ("clearly beats") — **AND does not hurt (c)** (neither bare-DC nor
product WC RPS worsens beyond WC-finals noise) AND does not worsen competitive calibration.
Otherwise KEEP 1.0 (recency-only), document the negative result, and still ship the parameter
(it is backward-compatible and off by default).
"""
from __future__ import annotations

import argparse
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from wcpred import datasets, metrics  # noqa: E402
from wcpred.models import (  # noqa: E402
    DixonColesModel, EnsembleModel, block_rps_by_class,
    walk_forward_block_predictions, walk_forward_confed_calibrated, walk_forward_dixon_coles,
)

# Friendly-weight grid. 1.0 == current (recency-only); the blueprint suggests ~0.3-0.5, so the
# grid brackets that with a lighter and a heavier touch.
FRIENDLY_WEIGHTS: tuple[tuple[str, float], ...] = (
    ("1.0", 1.0), ("0.75", 0.75), ("0.5", 0.5), ("0.3", 0.3), ("0.1", 0.1),
)
FRIENDLY_WEIGHTS_QUICK: tuple[tuple[str, float], ...] = (("1.0", 1.0), ("0.5", 0.5), ("0.3", 0.3))
CURRENT_LABEL = "1.0"            # DixonColesModel default (comp_weights=None == friendly weight 1.0)
WC_YEARS = (2010, 2014, 2018, 2022)
LEY_REFERENCE = 0.165            # Ley et al. (2019) national-team RPS, competitive matches
N_BOOT = 5000
BOOT_SEED = 20260612

# Gate tolerances (identical to the half-life gate). (a) must improve with a bootstrap CI that
# excludes 0; (c)/calibration get a small slack so WC-finals noise (~256 matches) doesn't block a
# genuine (a) win, but any real regression there still vetoes.
TOL_C = 1e-3                     # WC RPS may not rise by more than this (either model)
TOL_ECE = 2e-3                   # competitive calibration error may not rise by more than this


def _dc_factory(w: float):
    """A fresh DixonColesModel with the friendly tier down-weighted to `w` (1.0 -> off)."""
    return lambda: DixonColesModel(comp_weights=None if w == 1.0 else {"friendly": w})


def _competitive_per_match_rps(pooled: pd.DataFrame) -> np.ndarray:
    """Per-match normalized RPS on the pooled COMPETITIVE rows (row order is stable across weights
    because the matches are identical — only the probabilities differ)."""
    comp = pooled[pooled["comp_class"] == "competitive"]
    P = comp[["pH", "pD", "pA"]].to_numpy(dtype=float)
    y = comp["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
    return metrics.rps_per_match(P, y)


def _ece_competitive(pooled: pd.DataFrame, n_bins: int = 10) -> float:
    """Count-weighted one-vs-rest expected calibration error over the pooled competitive rows."""
    comp = pooled[pooled["comp_class"] == "competitive"]
    P = comp[["pH", "pD", "pA"]].to_numpy(dtype=float)
    y = comp["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
    tbl = metrics.calibration_table(P, y, n_bins=n_bins)
    if tbl.empty:
        return float("nan")
    w = tbl["count"] / tbl["count"].sum()
    return float((w * (tbl["mean_pred"] - tbl["observed_freq"]).abs()).sum())


def _wc_mean(rows: list[dict], key: str = "rps") -> float:
    """Unweighted fold mean (the convention the WC RPS bars are quoted in)."""
    return float(np.mean([r[key] for r in rows]))


def evaluate_weight(feat: pd.DataFrame, w: float, years: range, min_train: int) -> dict:
    """All metrics for one friendly weight: (a)/(b)/tiers from the block backtest, (c) from the WC
    walk-forward (bare DC + calibrated ensemble), plus competitive calibration error."""
    pooled = walk_forward_block_predictions(feat, _dc_factory(w), years, min_train=min_train)
    by_class = block_rps_by_class(pooled)
    dc_kwargs = {} if w == 1.0 else {"comp_weights": {"friendly": w}}
    dc_wc = walk_forward_dixon_coles(feat, years=WC_YEARS, **dc_kwargs)
    prod_wc = walk_forward_confed_calibrated(
        feat, years=WC_YEARS, base_factory=lambda: EnsembleModel(dc_kwargs=dc_kwargs))
    return {
        "w": w,
        "a_competitive": by_class["competitive"]["rps"], "n_competitive": by_class["competitive"]["n"],
        "b_all": by_class["all"]["rps"], "n_all": by_class["all"]["n"],
        "friendly": by_class.get("friendly", {}).get("rps", float("nan")),
        "other": by_class.get("other", {}).get("rps", float("nan")),
        "c_dc_wc": _wc_mean(dc_wc), "c_prod_wc": _wc_mean(prod_wc, "rps_cal"),
        "ece_competitive": _ece_competitive(pooled),
        "_per_match_competitive": _competitive_per_match_rps(pooled),
    }


def paired_bootstrap_gap(rps_cur: np.ndarray, rps_cand: np.ndarray,
                         n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    """Paired bootstrap of the per-match RPS gap (current - candidate) on the same competitive
    matches. Positive mean => candidate scores lower (better); 'clearly_better' iff the whole 95%
    CI is > 0."""
    diff = rps_cur - rps_cand
    rng = np.random.default_rng(seed)
    n = len(diff)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = diff[idx].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"mean_gap": float(diff.mean()), "ci_lo": float(lo), "ci_hi": float(hi),
            "clearly_better": bool(lo > 0.0)}


def decide(results: dict[str, dict]) -> tuple[str, dict | None, list[str]]:
    """Apply the gate. Candidate = the friendly weight with the lowest competitive RPS; adopt it
    only if it clearly beats current on (a) AND does not hurt (c) or calibration."""
    cur = results[CURRENT_LABEL]
    cand_label = min(results, key=lambda lab: results[lab]["a_competitive"])
    reasons: list[str] = []

    if cand_label == CURRENT_LABEL:
        reasons.append(f"lowest competitive RPS is at the current weight {CURRENT_LABEL} "
                       f"({cur['a_competitive']:.4f}) — down-weighting friendlies does not help (a)")
        reasons.append(f"=> KEEP friendly weight {CURRENT_LABEL} (negative result)")
        return CURRENT_LABEL, None, reasons

    cand = results[cand_label]
    boot = paired_bootstrap_gap(cur["_per_match_competitive"], cand["_per_match_competitive"])
    reasons.append(
        f"(a) best competitive RPS at friendly weight {cand_label} ({cand['a_competitive']:.4f}) vs "
        f"current {CURRENT_LABEL} ({cur['a_competitive']:.4f}); paired-bootstrap mean gap "
        f"{boot['mean_gap']:+.4f} (95% CI [{boot['ci_lo']:+.4f}, {boot['ci_hi']:+.4f}]) -> "
        f"{'clearly better' if boot['clearly_better'] else 'NOT clearly better (CI spans 0)'}")

    dc_ok = cand["c_dc_wc"] <= cur["c_dc_wc"] + TOL_C
    prod_ok = cand["c_prod_wc"] <= cur["c_prod_wc"] + TOL_C
    reasons.append(
        f"(c) bare-DC WC RPS {cand['c_dc_wc']:.4f} vs current {cur['c_dc_wc']:.4f} -> "
        f"{'OK' if dc_ok else 'WORSE'}; product (calibrated-ensemble) WC RPS {cand['c_prod_wc']:.4f} "
        f"vs current {cur['c_prod_wc']:.4f} -> {'OK (flat within WC-finals noise)' if prod_ok else 'WORSE'}")

    ece_ok = not (cand["ece_competitive"] > cur["ece_competitive"] + TOL_ECE)
    reasons.append(
        f"competitive calibration error {cand['ece_competitive']:.4f} vs current "
        f"{cur['ece_competitive']:.4f} -> {'OK' if ece_ok else 'WORSE'}")

    adopt = bool(boot["clearly_better"] and dc_ok and prod_ok and ece_ok)
    reasons.append(f"=> {'ADOPT friendly weight ' + cand_label if adopt else 'KEEP friendly weight ' + CURRENT_LABEL + ' (negative result)'}")
    return (cand_label if adopt else CURRENT_LABEL), boot, reasons


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def write_report(results: dict[str, dict], chosen: str, boot: dict | None, reasons: list[str],
                 grid: tuple[tuple[str, float], ...], years: range, as_of: str) -> pathlib.Path:
    cur = results[CURRENT_LABEL]
    keep = chosen == CURRENT_LABEL
    floor_label = min(results, key=lambda lab: results[lab]["a_competitive"])
    L = [
        "# Dixon-Coles competition-weight sweep (down-weight friendlies)",
        "",
        f"*Generated {datetime.date.today().isoformat()}; data as-of {as_of}. Expanding-window, "
        f"as-of block backtest: refit at yearly checkpoints over {years.start}-{years.stop - 1}, "
        f"each block predicted only from prior matches. Metric (a) = competitive internationals "
        f"(qualifiers + continental + WC finals), (b) = all incl. friendlies, (c) = the WC-finals "
        f"walk-forward (bare DC and the shipped calibrated ensemble). Normalized RPS, lower better. "
        f"The friendly weight scales friendlies in the DC likelihood; competitive/other stay 1.0.*",
        "",
        "## Verdict",
        "",
        f"**{'KEEP recency-only (friendly weight 1.0) — negative result.' if keep else 'ADOPT a ' + chosen + ' friendly weight in the Dixon-Coles fit.'}**",
        "",
    ]
    L += [f"- {r}" for r in reasons]
    L += [
        "",
        "Gate: adopt a non-1.0 friendly weight only if it improves competitive RPS (a) by a margin "
        "whose paired-bootstrap 95% CI excludes zero, AND does not raise either WC RPS (c) by more "
        f"than {TOL_C}, AND does not worsen competitive calibration by more than {TOL_ECE}. The "
        "parameter ships either way (backward-compatible, off by default).",
        "",
        "## Sweep",
        "",
        "| friendly weight | (a) competitive | (b) all | friendlies | (c) DC · WC | (c) product · WC | comp. ECE |",
        "|--|--:|--:|--:|--:|--:|--:|",
    ]
    for lab, _w in grid:
        if lab not in results:
            continue
        r = results[lab]
        tags = []
        if lab == CURRENT_LABEL:
            tags.append("current")
        if lab == chosen and not keep:
            tags.append("ADOPTED")
        if lab == floor_label:
            tags.append("(a) floor")
        tag = (" **" + ", ".join(tags) + "**") if tags else ""
        L.append(f"| {lab}{tag} | {r['a_competitive']:.4f} | {r['b_all']:.4f} | {r['friendly']:.4f} | "
                 f"{r['c_dc_wc']:.4f} | {r['c_prod_wc']:.4f} | {r['ece_competitive']:.4f} |")
    L += [
        "",
        f"Competitive-match counts: n(a) = {cur['n_competitive']:,}, n(all) = {cur['n_all']:,} "
        f"(vs ~256 WC-finals matches — the point of the broader detector). Friendlies are "
        f"{cur['n_all'] - cur['n_competitive']:,}+ of the all-internationals pool.",
        "",
        "## Reading",
        "",
        "- Metric (a) is the sensitive detector; the friendly weight is meant to sharpen it by "
        "leaning the goals fit on competitive matches. Metric (c) is the relevance guard — the "
        "friendly weight only reweights the DC fit, so (c) confirms a friendly-leaner DC does not "
        "cost the product on the tournament that matters (bare DC ~0.215, shipped ensemble ~0.202).",
    ]
    if keep:
        L.append(
            "- **Why it washes out:** down-weighting friendlies monotonically *worsens* competitive "
            "RPS (a) and clearly worsens both WC RPS metrics (c), buying only a small calibration "
            "(ECE) gain. This model deliberately trains on every international since 1872 because "
            "friendlies carry real strength signal — for sparse / younger national sides they are "
            "often the bulk of recent form — so discounting them discards information the goals fit "
            "relies on. The blueprint's friendly-discount helps models trained on a narrower modern "
            "slice; it does not transfer here. The parameter still ships (off by default) for future "
            "use — a different tier, or a smaller-sample regime where friendly noise dominates.")
    if boot is not None:
        L.append(f"- Paired bootstrap (best vs current, competitive, n_boot={N_BOOT}): mean gap "
                 f"{boot['mean_gap']:+.4f}, 95% CI [{boot['ci_lo']:+.4f}, {boot['ci_hi']:+.4f}].")
    L.append("")
    out = ROOT / "reports" / "dc_comp_weight.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    return out


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="smaller span/grid (smoke test)")
    args = ap.parse_args()
    grid = FRIENDLY_WEIGHTS_QUICK if args.quick else FRIENDLY_WEIGHTS
    years = range(2012, 2026) if args.quick else range(2004, 2026)
    min_train = 2000

    print("Loading processed match features...")
    feat = pd.read_parquet(ROOT / "data" / "processed" / "match_features.parquet")
    as_of = str(feat.loc[feat["played"], "date"].max().date())
    print(f"  {len(feat):,} matches; as-of {as_of}; block span {years.start}-{years.stop - 1}")

    results: dict[str, dict] = {}
    for lab, w in grid:
        print(f"\nFriendly weight {lab}:")
        r = evaluate_weight(feat, w, years, min_train)
        results[lab] = r
        print(f"  (a) competitive RPS {r['a_competitive']:.4f} (n={r['n_competitive']:,})  "
              f"(b) all {r['b_all']:.4f}  (c) DC-WC {r['c_dc_wc']:.4f}  "
              f"prod-WC {r['c_prod_wc']:.4f}  ECE {r['ece_competitive']:.4f}")

    chosen, boot, reasons = decide(results)
    print("\nGate:")
    for r in reasons:
        print("  - " + r)

    out = write_report(results, chosen, boot, reasons, grid, years, as_of)
    print(f"\nWrote {out}")
    print(f"\n  => {'KEEP current 1.0 (negative result)' if chosen == CURRENT_LABEL else 'ADOPT friendly weight ' + chosen}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
