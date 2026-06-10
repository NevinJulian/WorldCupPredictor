"""First real WC 2026 forecast from the trained ensemble.

    python scripts/08_forecast_2026.py [--sims 20000]

Scorelines come from Dixon-Coles, reweighted so each match's H/D/A marginals match the
calibrated ensemble (GBM + DC) outcome probabilities — so the sim inherits the outcome edge
(the ensemble's normalized RPS is 0.2036 vs DC-alone 0.2147). The group stage uses the real
2026 fixtures (with host advantage); knockout pairs are scored on neutral ground.

Output (data/processed/):
    wc2026_forecast_odds.csv  — per-team advance / R16 / QF / SF / Final / title probabilities

NOTE: deep-run / title odds are PROVISIONAL. The knockout bracket seeds qualifiers by
team strength into a standard bracket rather than FIFA's Annex-C third-place table (M4-2);
group-stage and `advance` probabilities are the trustworthy part.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import DATA_PROCESSED, forecast, tournament  # noqa: E402


def main(sims: int = 20000) -> int:
    print("Fitting the ensemble on all played data and assembling the 2026 forecast model...")
    model, sim_groups, display, info = forecast.build_forecast_model()
    if info["unresolved"]:
        print(f"  WARNING: unresolved team names {info['unresolved']} -> league-average fallback.")
    print(f"  ensemble weight w_gbm={info['ensemble_weight']:.2f}; "
          f"{info['n_group_fixtures']} real group fixtures + {info['n_pairs']} knockout pairs scored.")

    print(f"Simulating {sims:,} tournaments (outcome-reweighted Dixon-Coles)...")
    odds = tournament.simulate_tournament(sim_groups, model, n_sims=sims)
    odds["team"] = odds["team"].map(lambda t: display.get(t, t))
    odds = odds.rename(columns={"Winner": "title"})

    out = DATA_PROCESSED / "wc2026_forecast_odds.csv"
    cols = ["team", "win_group", "runner_up", "advance", "R16", "QF", "SF", "Final", "title"]
    odds[cols].to_csv(out, index=False)

    print("\nTop 16 title contenders (deep-run odds PROVISIONAL — Annex-C bracket pending):")
    show = odds.head(16)[["team", "advance", "R16", "QF", "SF", "Final", "title"]]
    print(show.to_string(index=False))

    title_sum = float(odds["title"].sum())
    advance_sum = float(odds["advance"].sum())
    top = odds.iloc[0]
    print("\nsanity checks:")
    print(f"  title probabilities sum to {title_sum:.3f}  (expect ~1.0 — one champion per sim)")
    print(f"  advance probabilities sum to {advance_sum:.1f}  (expect 32.0 — qualifiers per sim)")
    print(f"  top favourite: {top['team']} at {top['title']:.1%}  (sanity band ~10-25%)")
    print(f"\nFull table -> {out}")
    return 0


if __name__ == "__main__":
    n = 20000
    if "--sims" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sims") + 1])
    raise SystemExit(main(n))
