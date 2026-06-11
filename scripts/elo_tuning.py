"""Tune the Elo hyperparameters, then confirm transfer on the held-out WC backtest.

    python scripts/elo_tuning.py            # full grid + held-out confirmation
    python scripts/elo_tuning.py --quick    # tiny grid (smoke test)

What it does, and why it is leakage-free
----------------------------------------
The in-house Elo (`wcpred.elo`) still uses the eloratings.net defaults (home_adv=100, the
20/40/50/60 K-tiers, the 1/1.5/1.75/+1/8 goal-difference curve). This tunes three knobs —
``home_adv``, ``k_scale`` (an overall multiplier on the tier K weights) and ``gd_strength``
(scales the goal-difference multiplier's excess over 1) — and decides, by an explicit rule,
whether to adopt them as the new defaults.

1. TUNING (never touches the World Cups). For every grid point we recompute as-of Elo over
   **only pre-2010 matches**, then run an expanding-window validation that *ends before 2010*:
   for each fold year Y in `VAL_YEARS`, fit the Elo-logistic H/D/A map on matches dated < Y
   (as-of) and predict that year's matches. Predictions are pooled across the fold years and
   scored with the normalised RPS. The winner minimises that pooled validation RPS. Because
   the Elo pass is fed only pre-2010 rows and each fold trains strictly on its past, no
   2010+ (WC-backtest) information can reach the tuner.

2. HELD-OUT CONFIRMATION (the WC backtest, used ONLY here). With the winner frozen we rebuild
   the full feature table under both the default and the tuned Elo, then walk forward over the
   2010-2022 World Cups, reporting per-WC + average RPS for the Elo-logistic baseline (bar
   0.2045), the ensemble, and the confederation-calibrated ensemble (current 0.2019), plus the
   inter-confederation calibration gap.

3. DECISION. Adopt the tuned params as the new defaults ONLY if they improve BOTH the
   validation RPS AND the held-out WC RPS (or leave the WC unchanged), the WC gain is not
   driven by a single fold, and the confederation gap does not worsen. Otherwise keep the
   defaults and document the negative result. The verdict + tables are written to
   reports/elo_tuning.md.
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

from wcpred import clean, datasets, elo, features, metrics  # noqa: E402
from wcpred.models import (  # noqa: E402
    ConfederationCalibrator, EloLogisticModel, EnsembleModel,
)

WC_YEARS = (2010, 2014, 2018, 2022)
VAL_YEARS = tuple(range(1996, 2010))   # expanding-window validation folds — all end before 2010
BAR_ELO = 0.2045        # pure-Elo-logistic baseline (PLAN.md §7)
BAR_CAL = 0.2019        # confederation-calibrated ensemble (the current shipped headline)

# Coarse grid (~3 values/param -> small search space, large eval = low overfit risk).
GRID_FULL = {
    "home_adv": (50.0, 75.0, 100.0, 125.0),
    "k_scale": (0.75, 1.0, 1.5),
    "gd_strength": (0.5, 1.0, 1.5),
}
GRID_QUICK = {"home_adv": (75.0, 100.0), "k_scale": (1.0,), "gd_strength": (1.0, 1.5)}
DEFAULT_PARAMS = {"home_adv": 100.0, "k_scale": 1.0, "gd_strength": 1.0}

_WIN_SHARE = {"H": (1.0, 0.0), "D": (0.5, 0.5), "A": (0.0, 1.0)}


# --------------------------------------------------------------------------- #
# 1. Tuning — pooled pre-2010 expanding-window Elo-logistic RPS
# --------------------------------------------------------------------------- #
def validation_rps(matches: pd.DataFrame, params: dict, val_years=VAL_YEARS) -> tuple[float, int]:
    """Pooled normalised RPS of the Elo-logistic map over expanding folds that end before 2010.

    Elo is recomputed over pre-2010 matches only, so the tuner never sees a 2010+ row; each
    fold trains strictly on its own past (as-of). Returns (pooled_rps, n_pooled).
    """
    pre = matches[matches["year"] < 2010]   # the tuner never sees a 2010+ row
    elo_df, _ = elo.compute_elo(pre, **params)
    played = elo_df[elo_df["played"]].copy()
    probs, ys = [], []
    for y in val_years:
        lo, hi = pd.Timestamp(f"{y}-01-01"), pd.Timestamp(f"{y + 1}-01-01")
        train = played[played["date"] < lo]
        val = played[(played["date"] >= lo) & (played["date"] < hi)]
        if len(train) < 200 or val.empty:
            continue
        model = EloLogisticModel().fit(train)
        probs.append(model.predict_proba(val))
        ys.append(val["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy())
    P = np.vstack(probs)
    Y = np.concatenate(ys)
    return metrics.rps(P, Y), int(len(Y))


def grid_search(matches: pd.DataFrame, grid: dict) -> pd.DataFrame:
    keys = list(grid)
    rows = []
    combos = list(itertools.product(*(grid[k] for k in keys)))
    for i, combo in enumerate(combos, 1):
        params = dict(zip(keys, combo))
        rps, n = validation_rps(matches, params)
        rows.append({**params, "val_rps": rps, "n": n})
        tag = " ".join(f"{k}={params[k]}" for k in keys)
        print(f"  [{i:2d}/{len(combos)}] {tag:<48s} val_rps={rps:.4f}  (n={n})")
    return pd.DataFrame(rows).sort_values("val_rps").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 2. Held-out confirmation — the WC backtest (used only here)
# --------------------------------------------------------------------------- #
def _confed_gap(proba: np.ndarray, df: pd.DataFrame) -> tuple[float, dict]:
    """Mean |per-confederation residual win-share| over inter-confederation matches.

    The residual for a confederation is mean(actual_win_share - predicted_win_share) across
    every appearance in an inter-confederation match; the 'gap' is the mean of |residual| over
    confederations with >= 10 such appearances. Lower = better cross-confederation calibration.
    """
    hc = df["home_confed"].to_numpy()
    ac = df["away_confed"].to_numpy()
    res = df["result"].to_numpy()
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for i in range(len(df)):
        if pd.isna(hc[i]) or pd.isna(ac[i]) or hc[i] == ac[i] or res[i] not in _WIN_SHARE:
            continue
        pH, pD, pA = proba[i]
        oh, oa = _WIN_SHARE[res[i]]
        for c, o, p in ((hc[i], oh, pH + 0.5 * pD), (ac[i], oa, pA + 0.5 * pD)):
            sums[c] = sums.get(c, 0.0) + (o - p)
            counts[c] = counts.get(c, 0) + 1
    resid = {c: sums[c] / counts[c] for c in sums if counts[c] >= 10}
    gap = float(np.mean([abs(v) for v in resid.values()])) if resid else float("nan")
    return gap, resid


def held_out(matches: pd.DataFrame, ranking, params: dict) -> dict:
    """Rebuild features under `params` and walk forward over 2010-2022.

    Reports per-WC + average RPS for the Elo-logistic baseline, the ensemble, and the
    confederation-calibrated ensemble, plus the pooled inter-confederation calibration gap.
    """
    with_elo, _ = elo.compute_elo(matches, **params)
    feat = features.build_features(with_elo, ranking=ranking)
    per_wc, pool_ens, pool_y, pool_df = [], [], [], []
    for year, train, test in datasets.walk_forward_tournaments(feat, WC_YEARS):
        p_elo = EloLogisticModel().fit(train).predict_proba(test)
        ens = EnsembleModel().fit(train)
        p_ens = ens.predict_proba(test)
        calib = ConfederationCalibrator().fit(train)
        p_cal = calib.adjust(p_ens, test["home_confed"].to_numpy(), test["away_confed"].to_numpy())
        y = test["result"].map(datasets.RESULT_TO_INT).astype(int).to_numpy()
        per_wc.append({
            "year": year, "n": int(len(test)),
            "rps_elo": metrics.rps(p_elo, y), "rps_ens": metrics.rps(p_ens, y),
            "rps_cal": metrics.rps(p_cal, y), "weight": ens.weight_,
        })
        pool_ens.append(p_ens); pool_y.append(y); pool_df.append(test)
        print(f"    {year}: elo={per_wc[-1]['rps_elo']:.4f} ens={per_wc[-1]['rps_ens']:.4f} "
              f"cal={per_wc[-1]['rps_cal']:.4f} (w={ens.weight_:.2f}, n={len(test)})")
    gap, resid = _confed_gap(np.vstack(pool_ens), pd.concat(pool_df, ignore_index=True))
    avg = lambda k: float(np.mean([r[k] for r in per_wc]))  # noqa: E731  (unweighted fold mean, as 0.2045 is)
    return {
        "per_wc": per_wc, "avg_elo": avg("rps_elo"), "avg_ens": avg("rps_ens"),
        "avg_cal": avg("rps_cal"), "gap": gap, "resid": resid,
    }


# --------------------------------------------------------------------------- #
# 3. Decision rule
# --------------------------------------------------------------------------- #
def decide(val_def, val_win, ho_def, ho_win) -> tuple[bool, list[str]]:
    """Keep tuned params only if they improve validation AND don't regress the WC backtest."""
    reasons = []
    val_better = val_win < val_def - 1e-6
    reasons.append(f"validation RPS {val_win:.4f} vs default {val_def:.4f} -> "
                   f"{'IMPROVES' if val_better else 'no improvement'}")

    # Held-out: headline is the calibrated ensemble (bar 0.2019); also watch the Elo baseline.
    wc_better_or_equal = ho_win["avg_cal"] <= ho_def["avg_cal"] + 1e-4
    reasons.append(f"held-out WC RPS (calibrated) {ho_win['avg_cal']:.4f} vs default "
                   f"{ho_def['avg_cal']:.4f} -> {'OK' if wc_better_or_equal else 'WORSE'}")

    # WC gain must not be a single-fold artefact: tuned should win (or tie) a majority of folds,
    # not ride one lucky fold. (Negative delta = tuned better on that WC.)
    deltas = [w["rps_cal"] - d["rps_cal"] for w, d in zip(ho_win["per_wc"], ho_def["per_wc"])]
    n_better = sum(d < -1e-4 for d in deltas)
    n_worse = sum(d > 1e-4 for d in deltas)
    robust = n_better >= n_worse
    reasons.append(f"per-WC calibrated deltas (tuned-default) {[round(d, 4) for d in deltas]} -> "
                   f"tuned better on {n_better}/{len(deltas)}, worse on {n_worse}/{len(deltas)} "
                   f"({'robust across folds' if robust else 'single-fold-driven'})")

    gap_ok = not (ho_win["gap"] > ho_def["gap"] + 1e-4)
    reasons.append(f"confederation gap {ho_win['gap']:.4f} vs default {ho_def['gap']:.4f} -> "
                   f"{'OK' if gap_ok else 'WORSE'}")

    keep = bool(val_better and wc_better_or_equal and robust and gap_ok)
    return keep, reasons


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def _wc_table(label: str, ho: dict) -> list[str]:
    L = [f"**{label}**", "",
         "| WC | n | Elo-logistic | Ensemble | Calibrated ens | ens weight |",
         "|--|--:|--:|--:|--:|--:|"]
    for r in ho["per_wc"]:
        L.append(f"| {r['year']} | {r['n']} | {r['rps_elo']:.4f} | {r['rps_ens']:.4f} | "
                 f"{r['rps_cal']:.4f} | {r['weight']:.2f} |")
    L.append(f"| **avg** |  | **{ho['avg_elo']:.4f}** | **{ho['avg_ens']:.4f}** | "
             f"**{ho['avg_cal']:.4f}** |  |")
    L.append(f"| confed gap |  |  | **{ho['gap']:.4f}** |  |  |")
    L.append("")
    return L


def write_report(grid_df, best, val_def, ho_def, ho_win, keep, reasons, as_of):
    L = [
        "# Elo hyperparameter tuning",
        "",
        f"*Generated {datetime.date.today().isoformat()}; data as-of {as_of}. "
        f"Validation: pooled normalised RPS of the Elo-logistic map over expanding folds "
        f"{VAL_YEARS[0]}-{VAL_YEARS[-1]} (all end before 2010, never the World Cups). "
        f"Held-out: the 2010-2022 WC backtest (used only for confirmation).*",
        "",
        "## Verdict",
        "",
        f"**{'ADOPT the tuned parameters as new defaults.' if keep else 'KEEP the eloratings.net defaults (negative result).'}**",
        "",
        f"- Default params: `home_adv=100, k_scale=1.0, gd_strength=1.0`",
        f"- Best on validation: `home_adv={best['home_adv']}, k_scale={best['k_scale']}, "
        f"gd_strength={best['gd_strength']}` (val RPS {best['val_rps']:.4f} vs default {val_def:.4f})",
        "",
        "Decision checklist:",
        "",
    ]
    L += [f"- {r}" for r in reasons]
    L += ["",
          "Keep-rule: adopt only if the tuned params improve BOTH the validation RPS AND the "
          "held-out WC RPS (or leave it unchanged), the WC gain is not single-fold-driven, and "
          "the confederation gap does not worsen.",
          "",
          "## Held-out WC backtest (2010-2022)",
          "",
          f"Bars: Elo-logistic baseline **{BAR_ELO}**, calibrated ensemble **{BAR_CAL}**. "
          "RPS is the unweighted mean over the four WCs (matching how the 0.2045 bar is quoted).",
          ""]
    L += _wc_table("Default Elo (home_adv=100, k_scale=1.0, gd_strength=1.0)", ho_def)
    L += _wc_table(f"Tuned Elo (home_adv={best['home_adv']}, k_scale={best['k_scale']}, "
                   f"gd_strength={best['gd_strength']})", ho_win)
    L += ["## Validation grid (pooled pre-2010 RPS, lower is better)", "",
          "| home_adv | k_scale | gd_strength | val RPS | n |",
          "|--:|--:|--:|--:|--:|"]
    for _, r in grid_df.iterrows():
        star = "  ⭐" if (r["home_adv"] == best["home_adv"] and r["k_scale"] == best["k_scale"]
                          and r["gd_strength"] == best["gd_strength"]) else ""
        L.append(f"| {r['home_adv']:.0f} | {r['k_scale']:.2f} | {r['gd_strength']:.2f} | "
                 f"{r['val_rps']:.4f}{star} | {int(r['n'])} |")
    L.append("")
    out = ROOT / "reports" / "elo_tuning.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {out}")


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="tiny grid (smoke test)")
    args = ap.parse_args()
    grid = GRID_QUICK if args.quick else GRID_FULL

    print("Loading & cleaning matches...")
    matches = clean.load_clean_results()
    ranking = features.load_fifa_ranking()
    as_of = str(matches.loc[matches["played"], "date"].max().date())
    print(f"  {len(matches):,} matches; as-of {as_of}")

    print(f"\n1) Grid search — pooled validation RPS over folds {VAL_YEARS[0]}-{VAL_YEARS[-1]} "
          f"(ends before 2010):")
    grid_df = grid_search(matches, grid)
    best = grid_df.iloc[0].to_dict()
    val_def = float(grid_df[(grid_df.home_adv == 100.0) & (grid_df.k_scale == 1.0)
                            & (grid_df.gd_strength == 1.0)]["val_rps"].iloc[0]) \
        if ((grid_df.home_adv == 100.0) & (grid_df.k_scale == 1.0)
            & (grid_df.gd_strength == 1.0)).any() else validation_rps(matches, DEFAULT_PARAMS)[0]
    best_params = {k: best[k] for k in ("home_adv", "k_scale", "gd_strength")}
    print(f"\n  Best validation: {best_params}  val_rps={best['val_rps']:.4f}  "
          f"(default {val_def:.4f})")

    print("\n2) Held-out WC backtest — DEFAULT Elo:")
    ho_def = held_out(matches, ranking, DEFAULT_PARAMS)
    if best_params == DEFAULT_PARAMS:
        print("\n  Winner == default; held-out tuned run skipped.")
        ho_win = ho_def
    else:
        print("\n   Held-out WC backtest — TUNED Elo:")
        ho_win = held_out(matches, ranking, best_params)

    keep, reasons = decide(val_def, best["val_rps"], ho_def, ho_win)
    print("\n3) Decision:")
    for r in reasons:
        print(f"  - {r}")
    print(f"\n  => {'ADOPT tuned params' if keep else 'KEEP defaults (negative result)'}")

    write_report(grid_df, best, val_def, ho_def, ho_win, keep, reasons, as_of)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
