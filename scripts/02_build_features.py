"""Build the modelling table: data/processed/match_features.parquet

    python scripts/02_build_features.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, clean, elo, features  # noqa: E402


def main() -> int:
    print("1/4  Loading & cleaning matches...")
    matches = clean.load_clean_results()
    print(f"     {len(matches):,} matches, {matches['date'].dt.year.min()}-{matches['date'].dt.year.max()}")

    print("2/4  Computing World Football Elo (as-of)...")
    with_elo, model = elo.compute_elo(matches)

    print("3/4  Loading FIFA ranking + engineering features...")
    ranking = features.load_fifa_ranking()
    if ranking is None:
        print("     (no ranking file — rank features skipped)")
    feat = features.build_features(with_elo, ranking=ranking)

    print("4/4  Saving...")
    out = DATA_PROCESSED / "match_features.parquet"
    try:
        feat.to_parquet(out, index=False)
    except Exception as e:  # pyarrow missing
        out = out.with_suffix(".csv")
        feat.to_csv(out, index=False)
        print(f"     (parquet failed: {e}; wrote CSV instead)")
    elo.current_ratings_table(model).to_csv(DATA_PROCESSED / "current_elo.csv", index=False)
    feat[feat["played"]].tail(3000).to_csv(DATA_PROCESSED / "match_features_sample.csv", index=False)

    fc = features.feature_columns(feat)
    print(f"\nDone -> {out}")
    print(f"  rows: {len(feat):,}  |  feature columns: {len(fc)}")
    print(f"  features: {', '.join(fc[:12])}{' ...' if len(fc) > 12 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
