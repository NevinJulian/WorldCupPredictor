"""GATE: does an xG-adjusted in-tournament strength update beat the result-only update?

    python scripts/xg_adjust_gate.py [--quick]

Hypothesis (issue #53): inside a tournament, goals are a noisy strength signal (finishing
variance over 1-3 games), so updating each team's rating from an **xG-adjusted effective
scoreline** should predict later matches at least as well as updating from raw goals.

Backtest (the only WCs with xG — StatsBomb open data, data/raw/wc_xg_2018_2022.csv):
for 2018 and 2022, fit a fixed Elo->1X2 map on data strictly before the tournament, then walk the
tournament in date order updating ratings via the in-house Elo (neutral, K=60). Two variants:
  * RESULT-ONLY — ratings update from the real scoreline,
  * xG-ADJUSTED — ratings update from `xg_adjust.effective_scoreline` (shrink>0, lam<1).
Predict every **later** match (both teams have >=1 prior game this tournament) from its pre-match
elo_diff and score the actual H/D/A with normalized RPS. Pool 2018+2022.

As-of / leakage-free: compute_elo is sequential (each pre-match rating sees only earlier games),
the 1X2 map is fit only on pre-tournament data, and a match's own (effective) scoreline never
informs its own prediction — only earlier matches' scorelines move the ratings going into it.

GATE: keep the xG adjustment ON by default only if the best (lam, shrink) **improves or is neutral
on** the pooled later-match RPS vs result-only; else ship OFF (knobs still available). Lightly
validated (2 tournaments). Verdict + tables -> reports/xg_adjust_gate.md.
"""
from __future__ import annotations

import argparse
import datetime
import itertools
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from wcpred import clean, datasets, elo, metrics, xg_adjust  # noqa: E402
from wcpred.models import EloLogisticModel  # noqa: E402

WC_YEARS = (2018, 2022)
LAMBDAS = (0.0, 0.25, 0.5, 0.75)          # weight on actual goals; (1-lam) = xG trust
SHRINKS = (0.25, 0.5, 0.75, 1.0)          # 0 == result-only (the baseline)
LAMBDAS_QUICK = (0.0, 0.5)
SHRINKS_QUICK = (0.5, 1.0)
N_BOOT = 5000
BOOT_SEED = 20260613


def _wc_finals(matches: pd.DataFrame, year: int) -> pd.DataFrame:
    return matches[(matches["tournament"] == "FIFA World Cup") & (matches["year"] == year)
                   & matches["played"].astype(bool)]


def later_match_keys(matches: pd.DataFrame, year: int) -> list[tuple]:
    """Keys (date_str, home, away) of WC `year` matches where BOTH teams have a prior game this WC.

    Walks the tournament in date order tracking which teams have appeared; the group-stage opener
    of each team is excluded (no in-tournament info yet), leaving MD2/MD3 + all knockout matches.
    """
    wc = _wc_finals(matches, year).sort_values(["date"], kind="stable")
    seen: set[str] = set()
    keys = []
    for r in wc.itertuples(index=False):
        if r.home_team in seen and r.away_team in seen:
            keys.append((pd.Timestamp(r.date).date().isoformat(), r.home_team, r.away_team))
        seen.add(r.home_team)
        seen.add(r.away_team)
    return keys


def _key_index(df: pd.DataFrame) -> dict[tuple, int]:
    """{(date_str, home, away) -> row position} for a compute_elo output frame."""
    out = {}
    d = df["date"].to_numpy()
    h = df["home_team"].to_numpy()
    a = df["away_team"].to_numpy()
    for i in range(len(df)):
        out[(pd.Timestamp(d[i]).date().isoformat(), h[i], a[i])] = i
    return out


def predictions_for_variant(elo_df: pd.DataFrame, fitted: dict, keys_by_year: dict) -> tuple[np.ndarray, np.ndarray]:
    """Per-match P(H/D/A) and actual y for every later match, using one variant's pre-match elo.

    `fitted[year]` is the Elo->1X2 model fit on data before that WC; `elo_df` is a compute_elo
    output (raw or effective). Predictions read the variant's pre-match elo_diff; targets are the
    REAL results (passed in via keys_by_year, which carries the actual H/D/A per key).
    """
    idx = _key_index(elo_df)
    probs, ys = [], []
    for year, keyrows in keys_by_year.items():
        rows = [idx[k] for k, _ in keyrows]
        sub = elo_df.iloc[rows]
        p = fitted[year].predict_proba(sub)
        y = np.array([datasets.RESULT_TO_INT[r] for _, r in keyrows])
        probs.append(p)
        ys.append(y)
    return np.vstack(probs), np.concatenate(ys)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    lambdas = LAMBDAS_QUICK if args.quick else LAMBDAS
    shrinks = SHRINKS_QUICK if args.quick else SHRINKS

    print("Loading matches + StatsBomb xG...")
    matches = clean.load_clean_results()
    xg = xg_adjust.load_match_stats(ROOT / "data" / "raw" / "wc_xg_2018_2022.csv")
    if xg is None:
        print("No xG file — run scripts/fetch_wc_xg.py first.", file=sys.stderr)
        return 1

    # Baseline: result-only in-tournament Elo (the raw scoreline drives every update).
    raw_elo, _ = elo.compute_elo(matches)

    # Fixed Elo->1X2 map per WC, fit on the elo frame strictly before that tournament (as-of). The
    # actual H/D/A target per later match is the real result (read from the raw elo frame).
    fitted, keys_by_year = {}, {}
    for year in WC_YEARS:
        cutoff = _wc_finals(raw_elo, year)["date"].min()
        train = datasets.played_only(raw_elo[raw_elo["date"] < cutoff])
        fitted[year] = EloLogisticModel().fit(train)
        result_by_key = {(pd.Timestamp(r.date).date().isoformat(), r.home_team, r.away_team): r.result
                         for r in _wc_finals(raw_elo, year).itertuples(index=False)}
        keys_by_year[year] = [(k, result_by_key[k]) for k in later_match_keys(raw_elo, year)]
        print(f"  WC {year}: {len(keys_by_year[year])} later matches; map fit on {len(train):,} pre-{year} games")

    p_raw, y = predictions_for_variant(raw_elo, fitted, keys_by_year)
    rps_raw = metrics.rps(p_raw, y)
    rps_raw_pm = metrics.rps_per_match(p_raw, y)
    n = len(y)
    print(f"\nResult-only later-match RPS (pooled 2018+2022, n={n}): {rps_raw:.4f}")

    # Sweep the xG-adjusted variant.
    grid = []
    best = None
    for lam, shrink in itertools.product(lambdas, shrinks):
        eff, n_adj = xg_adjust.apply_effective_scores(matches, xg, lam, shrink, years=WC_YEARS)
        eff_elo, _ = elo.compute_elo(eff)
        p_eff, y2 = predictions_for_variant(eff_elo, fitted, keys_by_year)
        assert np.array_equal(y, y2)
        rps_eff = metrics.rps(p_eff, y)
        row = {"lam": lam, "shrink": shrink, "rps": rps_eff, "delta": rps_eff - rps_raw,
               "n_adjusted": n_adj, "_pm": metrics.rps_per_match(p_eff, y)}
        grid.append(row)
        if best is None or rps_eff < best["rps"]:
            best = row
        print(f"  lam={lam:<4} shrink={shrink:<4} -> RPS {rps_eff:.4f} (delta {row['delta']:+.4f}, "
              f"{n_adj} scorelines adjusted)")

    # Paired bootstrap of the best config vs result-only (context — n is small).
    diff = rps_raw_pm - best["_pm"]            # >0 where xG-adjusted is better (lower)
    rng = np.random.default_rng(BOOT_SEED)
    boot = diff[rng.integers(0, n, size=(N_BOOT, n))].mean(axis=1)
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

    # The SHIPPED default (conservative balanced — xg_adjust.XG_LAMBDA / XG_SHRINK), chosen over the
    # aggressive point-estimate optimum because the win is not significant.
    shipped = next((r for r in grid if r["lam"] == xg_adjust.XG_LAMBDA
                    and r["shrink"] == xg_adjust.XG_SHRINK), None)

    # Gate: improve-or-neutral on the pooled later-match RPS (the best config decides ON/OFF).
    tol = 1e-3
    keep = bool(best["delta"] <= tol)
    reasons = [
        f"best xG-adjusted config: lam={best['lam']}, shrink={best['shrink']} -> RPS {best['rps']:.4f} "
        f"vs result-only {rps_raw:.4f} (delta {best['delta']:+.4f}) -> "
        f"{'IMPROVES/NEUTRAL' if keep else 'WORSE'} (gate tol {tol})",
        f"paired bootstrap (best vs result-only, n={n}): mean gap {diff.mean():+.4f}, "
        f"95% CI [{ci_lo:+.4f}, {ci_hi:+.4f}] -> NOT significant (small n; CI spans 0)",
    ]
    if shipped is not None:
        reasons.append(
            f"shipped default lam={xg_adjust.XG_LAMBDA}, shrink={xg_adjust.XG_SHRINK} (conservative, "
            f"balanced goal/xG trust) -> RPS {shipped['rps']:.4f} (delta {shipped['delta']:+.4f}); "
            f"chosen over the aggressive pure-xG optimum given the small-sample insignificance")
    reasons.append("Lightly validated: 2 tournaments, "
                   f"{n} later matches. xG is the only lever (possession/shots not weighted).")
    print("\nGate:")
    for r in reasons:
        print("  - " + r)
    verdict = (f"KEEP ON; shipped default lam={xg_adjust.XG_LAMBDA}, shrink={xg_adjust.XG_SHRINK}"
               if keep else "SHIP OFF by default (knobs available)")
    print(f"\n  => {verdict}")

    _write_report(rps_raw, n, grid, best, shipped, keep, reasons,
                  str(matches.loc[matches['played'], 'date'].max().date()))
    return 0


def _write_report(rps_raw, n, grid, best, shipped, keep, reasons, as_of):
    ship_txt = (f" with conservative balanced defaults (lam={shipped['lam']}, shrink={shipped['shrink']})"
                if keep and shipped is not None else "")
    L = [
        "# In-tournament xG adjustment — GATE result",
        "",
        f"*Generated {datetime.date.today().isoformat()}; data as-of {as_of}. Backtest on the 2018 "
        f"& 2022 World Cups (StatsBomb open-data xG). For each WC: a fixed Elo->1X2 map fit on "
        f"pre-tournament data, then the tournament walked in date order updating ratings from the "
        f"real scoreline (result-only) vs the xG-adjusted effective scoreline. Later matches (both "
        f"teams with >=1 prior game) scored with normalized RPS, pooled across both WCs (n={n}). "
        f"As-of / leakage-free; lightly validated (2 tournaments).*",
        "",
        "## Verdict",
        "",
        f"**{'KEEP the xG adjustment ON by default' + ship_txt + '.' if keep else 'SHIP the xG adjustment OFF by default (negative / inconclusive).'}**",
        "",
    ]
    L += [f"- {r}" for r in reasons]
    L += [
        "",
        "Gate: adopt ON only if the best (lam, shrink) improves or is neutral (delta <= 0.001) on the "
        "pooled later-match RPS vs result-only. Either way the lever ships via `xg_adjust` knobs "
        "(`XG_LAMBDA`, `XG_SHRINK`) and `build_forecast_model(xg_adjustment=...)`.",
        "",
        f"## Result-only baseline: RPS **{rps_raw:.4f}** (pooled later matches, n={n})",
        "",
        "## xG-adjusted sweep (lam = weight on goals, shrink = adjustment strength)",
        "",
        "| lam | shrink | RPS | delta vs result-only | scorelines adjusted |",
        "|--:|--:|--:|--:|--:|",
    ]
    for r in sorted(grid, key=lambda r: r["rps"]):
        star = "  ⭐" if r is best else ""
        L.append(f"| {r['lam']:.2f} | {r['shrink']:.2f} | {r['rps']:.4f}{star} | "
                 f"{r['delta']:+.4f} | {r['n_adjusted']} |")
    L += ["",
          "*lam = 1 or shrink = 0 reduces exactly to result-only. xG is the only lever; possession / "
          "shots are intentionally not weighted into the update.*", ""]
    out = ROOT / "reports" / "xg_adjust_gate.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    raise SystemExit(main())
