"""Score the Dixon-Coles + GBM ensemble on the walk-forward World Cups, vs Elo and GBM.

    python scripts/07_ensemble.py

For each World Cup it trains (strictly before) the ensemble — whose mixing weight is chosen on
a time-based inner-val window, never the test fold — plus the Elo-logistic baseline, and reads
the ensemble's full-train GBM component as the standalone GBM. It reports per-WC + avg
normalized RPS for all three, and a paired-bootstrap 95% CI on the per-match RPS gap of the
ensemble vs Elo and vs GBM (pooled across all test matches). Writes a regenerable
data/processed/ensemble_rps.json.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, datasets, metrics, models  # noqa: E402


def paired_bootstrap(gap: np.ndarray, n_boot: int = 10000, seed: int = 0) -> tuple[float, float, float]:
    """Mean per-match gap and its percentile 95% CI by resampling matches with replacement."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(gap), size=(n_boot, len(gap)))
    boot = gap[idx].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(gap.mean()), float(lo), float(hi)


def main() -> int:
    fp = DATA_PROCESSED / "match_features.parquet"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/02_build_features.py first.")
    df = pd.read_parquet(fp)

    print(f"Loaded {len(df):,} matches; walk-forward fitting ensemble + baselines per World Cup...")
    per_wc, pooled = [], {"y": [], "ens": [], "elo": [], "gbm": []}
    for year, train, test in datasets.walk_forward_tournaments(df):
        ens = models.EnsembleModel().fit(train)
        elo = models.EloLogisticModel().fit(train)
        y = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        p_ens = ens.predict_proba(test)
        p_gbm = ens.gbm_.predict_proba(test)   # the standalone GBM (fit on full train)
        p_elo = elo.predict_proba(test)
        per_wc.append({
            "year": year, "n": int(len(test)), "weight": round(ens.weight_, 3),
            "ens": metrics.rps(p_ens, y), "elo": metrics.rps(p_elo, y), "gbm": metrics.rps(p_gbm, y),
        })
        pooled["y"].append(y)
        for k, p in (("ens", p_ens), ("elo", p_elo), ("gbm", p_gbm)):
            pooled[k].append(p)

    y = np.concatenate(pooled["y"])
    r_ens = metrics.rps_per_match(np.vstack(pooled["ens"]), y)
    r_elo = metrics.rps_per_match(np.vstack(pooled["elo"]), y)
    r_gbm = metrics.rps_per_match(np.vstack(pooled["gbm"]), y)
    avg = {"ens": float(r_ens.mean()), "elo": float(r_elo.mean()), "gbm": float(r_gbm.mean())}

    print("\nEnsemble vs baselines (normalized RPS — lower is better):")
    print(f"  {'WC':>6} {'n':>4} {'w_gbm':>6} {'Ensemble':>9} {'Elo':>8} {'GBM':>8}")
    for r in per_wc:
        print(f"  {r['year']:>6} {r['n']:>4} {r['weight']:>6.2f} "
              f"{r['ens']:>9.4f} {r['elo']:>8.4f} {r['gbm']:>8.4f}")
    print(f"  {'avg':>6} {'':>4} {'':>6} {avg['ens']:>9.4f} {avg['elo']:>8.4f} {avg['gbm']:>8.4f}")

    # Paired bootstrap on the per-match gap (negative = ensemble better).
    print("\nPaired-bootstrap 95% CI on the ensemble's per-match RPS gap (negative favours ensemble):")
    cis = {}
    for name, base in (("Elo", r_elo), ("GBM", r_gbm)):
        mean_gap, lo, hi = paired_bootstrap(r_ens - base)
        sig = "significant" if hi < 0 else ("worse" if lo > 0 else "not significant (CI spans 0)")
        cis[name] = {"mean_gap": round(mean_gap, 5), "ci95": [round(lo, 5), round(hi, 5)]}
        print(f"  vs {name:<3}: {mean_gap:+.5f}  95% CI [{lo:+.5f}, {hi:+.5f}]  -> {sig}")

    out = DATA_PROCESSED / "ensemble_rps.json"
    out.write_text(json.dumps({
        "model": "ensemble_dc_gbm",
        "metric": "rps",
        "convention": "standard normalized RPS (divide by r-1 = 2); lower is better",
        "split": "time-based walk_forward_tournaments; mixing weight tuned on an inner-val window",
        "per_wc": [{"year": r["year"], "n": r["n"], "weight": r["weight"],
                    "ens": round(r["ens"], 4), "elo": round(r["elo"], 4), "gbm": round(r["gbm"], 4)}
                   for r in per_wc],
        "average": {k: round(v, 4) for k, v in avg.items()},
        "paired_bootstrap_ci95": cis,
        "generated_by": "scripts/07_ensemble.py",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
