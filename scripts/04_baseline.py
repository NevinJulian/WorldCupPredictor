"""Compute and record the Elo-logistic baseline RPS — the bar every model must beat.

    python scripts/04_baseline.py

Reads data/processed/match_features.parquet, fits the minimal Elo-logistic outcome model
per World Cup (training strictly before each), scores normalized RPS, and writes
data/processed/baseline_rps.json. Prints the per-WC table.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, models  # noqa: E402


def build_record(rows: list[dict]) -> dict:
    """Assemble the JSON-serializable canonical-bar record from per-WC results."""
    per_wc = {str(r["year"]): round(r["rps"], 4) for r in rows}
    n_per_wc = {str(r["year"]): r["n"] for r in rows}
    average = round(sum(r["rps"] for r in rows) / len(rows), 4) if rows else None
    return {
        "model": "elo_logistic",
        "features": list(models.BASELINE_FEATURES),
        "metric": "rps",
        "convention": "standard normalized RPS (divide by r-1 = 2); lower is better",
        "split": "time-based walk_forward_tournaments (train strictly before each WC)",
        "per_wc": per_wc,
        "n_per_wc": n_per_wc,
        "average": average,
        "generated_by": "scripts/04_baseline.py",
    }


def main() -> int:
    fp = DATA_PROCESSED / "match_features.parquet"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/02_build_features.py first.")

    df = pd.read_parquet(fp)
    print(f"Loaded {len(df):,} matches; fitting Elo-logistic baseline per World Cup...")
    rows = models.walk_forward_elo_baseline(df)
    record = build_record(rows)

    out = DATA_PROCESSED / "baseline_rps.json"
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print("\nElo-logistic baseline (normalized RPS — the bar to beat):")
    print(f"  {'WC':>6} {'n':>4} {'RPS':>8}")
    for r in rows:
        print(f"  {r['year']:>6} {r['n']:>4} {r['rps']:>8.4f}")
    print(f"  {'avg':>6} {'':>4} {record['average']:>8.4f}")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
