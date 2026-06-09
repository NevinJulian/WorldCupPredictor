"""Score the gradient-boosted outcome model on the walk-forward World Cups, vs the Elo bar.

    python scripts/06_gbm_outcome.py

Reads data/processed/match_features.parquet, fits the isotonic-calibrated GBM H/D/A model per
World Cup (train strictly before each), scores normalized RPS, and prints the per-WC table
against the recorded Elo baseline (data/processed/baseline_rps.json). Writes a regenerable
data/processed/gbm_outcome_rps.json (not the canonical bar — that stays Elo).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, models  # noqa: E402


def main() -> int:
    fp = DATA_PROCESSED / "match_features.parquet"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/02_build_features.py first.")

    df = pd.read_parquet(fp)
    n_feat = len(models.gbm_feature_columns(df))
    print(f"Loaded {len(df):,} matches; fitting GBM outcome model ({n_feat} features) per World Cup...")
    rows = models.walk_forward_gbm_outcome(df)
    gbm = {str(r["year"]): round(r["rps"], 4) for r in rows}
    gbm_avg = round(sum(r["rps"] for r in rows) / len(rows), 4)

    bar_fp = DATA_PROCESSED / "baseline_rps.json"
    bar = json.loads(bar_fp.read_text(encoding="utf-8")) if bar_fp.exists() else {}
    bar_wc, bar_avg = bar.get("per_wc", {}), bar.get("average")

    print("\nGBM outcome vs Elo baseline (normalized RPS — lower is better):")
    print(f"  {'WC':>6} {'n':>4} {'GBM':>8} {'Elo':>8} {'delta':>8}")
    for r in rows:
        y = str(r["year"])
        elo = bar_wc.get(y)
        delta = f"{gbm[y] - elo:+.4f}" if elo is not None else "   n/a"
        elo_s = f"{elo:.4f}" if elo is not None else "  n/a"
        print(f"  {y:>6} {r['n']:>4} {gbm[y]:>8.4f} {elo_s:>8} {delta:>8}")
    avg_delta = f"{gbm_avg - bar_avg:+.4f}" if bar_avg is not None else "   n/a"
    bar_avg_s = f"{bar_avg:.4f}" if bar_avg is not None else "  n/a"
    print(f"  {'avg':>6} {'':>4} {gbm_avg:>8.4f} {bar_avg_s:>8} {avg_delta:>8}")
    if bar_avg is not None:
        verdict = "BEATS" if gbm_avg < bar_avg else "does not beat"
        print(f"\nGBM outcome {verdict} the Elo bar (avg {gbm_avg:.4f} vs {bar_avg:.4f}).")

    out = DATA_PROCESSED / "gbm_outcome_rps.json"
    out.write_text(json.dumps({
        "model": "gbm_outcome",
        "metric": "rps",
        "convention": "standard normalized RPS (divide by r-1 = 2); lower is better",
        "split": "time-based walk_forward_tournaments (train strictly before each WC)",
        "n_features": n_feat,
        "per_wc": gbm, "average": gbm_avg,
        "elo_bar_average": bar_avg,
        "generated_by": "scripts/06_gbm_outcome.py",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
