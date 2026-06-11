"""GATE: does a mean-preserving over-dispersion of the goals model improve goal calibration?

    python scripts/overdispersion_gate.py [--quick]

Hypothesis (PLAN / Step 4): the scoreline distribution is under-dispersed vs real football —
Poisson tails are thin. We add a mean-preserving negative-binomial over-dispersion `a` to the
Dixon-Coles marginals (same lambda, variance lambda*(1+a*lambda)) and RE-REWEIGHT each matrix to
the SAME W/D/L, so outcome probabilities are unchanged and only the spread of scorelines *within*
each outcome changes.

Why this is the right test. 1X2 RPS is invariant under any W/D/L-preserving reshaping, so it
cannot judge this lever. We instead score the **goal** distribution directly with proper scoring
rules on a held-out, time-based backtest: the negative log-likelihood of the **total goals** and of
the **exact scoreline**, plus an over-2.5 calibration check. The over-dispersion only changes the
score-matrix *shape*, not the DC *fit*, so we fit DC once per period and just toggle `a`; we reweight
the over-dispersed matrix to the Poisson matrix's own W/D/L, isolating the within-outcome effect.

Procedure (as-of throughout): a VALIDATION period picks `a` (grid) by minimising total-goals NLL;
a later, untouched TEST period confirms it. DC for each period is fit strictly on prior matches.

GATE — keep `a` only if, on the TEST period: total-goals NLL and exact-score NLL are both better or
no worse than Poisson, AND expected goals are preserved (W/D/L are preserved by construction). If the
best validation `a` is 0, or it does not transfer, DROP it (negative result) and ship Steps 1-3 only.
Verdict + tables -> reports/overdispersion_gate.md.
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

from wcpred import clean  # noqa: E402
from wcpred.forecast import reweight_to_outcome  # noqa: E402
from wcpred.models import DixonColesModel  # noqa: E402

ALPHAS = (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)
ALPHAS_QUICK = (0.0, 0.1, 0.2)
EPS = 1e-12
# as-of periods: fit DC strictly before each window; ~12y look-back is plenty (1.5y half-life).
VAL = ("2002-01-01", "2014-01-01", "2019-01-01")   # (fit_from, eval_lo, eval_hi)
TEST = ("2007-01-01", "2019-01-01", "2027-01-01")


def _hda(M: np.ndarray) -> tuple[float, float, float]:
    return float(np.tril(M, -1).sum()), float(np.trace(M)), float(np.triu(M, 1).sum())


def _matrices(dc: DixonColesModel, rows: pd.DataFrame):
    """Per match: the Poisson matrix (as-of fit). Reused across alphas (fit is alpha-independent)."""
    dc.overdispersion = 0.0
    out = []
    for r in rows.itertuples(index=False):
        neu = bool(getattr(r, "neutral", True))
        out.append((dc.score_matrix(r.home_team, r.away_team, neutral=neu),
                    int(r.home_score), int(r.away_score), neu, r.home_team, r.away_team))
    return out


def _score(M: np.ndarray, hs: int, as_: int) -> tuple[float, float, float, float]:
    """(exact-score NLL, total-goals NLL, P(over 2.5), E[total goals]) for one matrix vs actual."""
    G = M.shape[0]
    x, y = min(hs, G - 1), min(as_, G - 1)
    exact_nll = -np.log(max(M[x, y], EPS))
    totals = np.array([M[np.arange(max(0, k - G + 1), min(k, G - 1) + 1),
                         k - np.arange(max(0, k - G + 1), min(k, G - 1) + 1)].sum()
                       for k in range(2 * G - 1)])
    t = min(hs + as_, len(totals) - 1)
    total_nll = -np.log(max(totals[t], EPS))
    p_over = float(totals[3:].sum())
    e_tot = float((np.arange(len(totals)) * totals).sum())
    return exact_nll, total_nll, p_over, e_tot


def evaluate(pois_mats, alpha: float):
    """Score every match for a given alpha (alpha=0 -> Poisson; else NB reweighted to Poisson W/D/L)."""
    dc_nb = _DC_NB
    ex, tot, povers, overs, e_goals = [], [], [], [], []
    for M_pois, hs, as_, neu, h, a in pois_mats:
        if alpha <= 0.0:
            M = M_pois
        else:
            dc_nb.overdispersion = alpha
            M = reweight_to_outcome(dc_nb.score_matrix(h, a, neutral=neu), _hda(M_pois))
        e_nll, t_nll, p_over, e_tot = _score(M, hs, as_)
        ex.append(e_nll); tot.append(t_nll); povers.append(p_over)
        overs.append(1.0 if hs + as_ >= 3 else 0.0); e_goals.append(e_tot)
    return {"exact_nll": float(np.mean(ex)), "total_nll": float(np.mean(tot)),
            "pred_over": float(np.mean(povers)), "obs_over": float(np.mean(overs)),
            "e_goals": float(np.mean(e_goals)), "n": len(ex)}


def fit_dc(matches: pd.DataFrame, fit_from: str, lo: str) -> tuple[DixonColesModel, pd.DataFrame]:
    train = matches[(matches["date"] >= pd.Timestamp(fit_from)) & (matches["date"] < pd.Timestamp(lo))]
    return DixonColesModel().fit(train), train


def period_rows(matches: pd.DataFrame, lo: str, hi: str) -> pd.DataFrame:
    return matches[(matches["date"] >= pd.Timestamp(lo)) & (matches["date"] < pd.Timestamp(hi))].copy()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    alphas = ALPHAS_QUICK if args.quick else ALPHAS

    print("Loading matches...")
    m = clean.load_clean_results()
    m = m[m["played"] & m["home_score"].notna() & m["away_score"].notna()].copy()

    global _DC_NB
    # --- validation: pick alpha ---
    print(f"Fitting DC for validation (<{VAL[1]})...")
    dc_v, _ = fit_dc(m, *VAL[:2])
    _DC_NB = dc_v
    val_rows = period_rows(m, VAL[1], VAL[2])
    pois_v = _matrices(dc_v, val_rows)
    print(f"Validation matches {VAL[1]}..{VAL[2]}: {len(pois_v)}")
    val = {a: evaluate(pois_v, a) for a in alphas}
    for a in alphas:
        print(f"  a={a:<4}  total_nll={val[a]['total_nll']:.4f}  exact_nll={val[a]['exact_nll']:.4f}")
    best_a = min(alphas, key=lambda a: val[a]["total_nll"])
    print(f"  -> best validation alpha = {best_a} (total_nll {val[best_a]['total_nll']:.4f} "
          f"vs Poisson {val[0.0]['total_nll']:.4f})")

    # --- test: confirm best_a vs Poisson ---
    print(f"\nFitting DC for test (<{TEST[1]})...")
    dc_t, _ = fit_dc(m, *TEST[:2])
    _DC_NB = dc_t
    test_rows = period_rows(m, TEST[1], TEST[2])
    pois_t = _matrices(dc_t, test_rows)
    print(f"Test matches {TEST[1]}..{TEST[2]}: {len(pois_t)}")
    base = evaluate(pois_t, 0.0)
    nb = evaluate(pois_t, best_a) if best_a > 0 else base

    # --- gate ---
    d_total = nb["total_nll"] - base["total_nll"]
    d_exact = nb["exact_nll"] - base["exact_nll"]
    d_egoals = abs(nb["e_goals"] - base["e_goals"])
    tol = 1e-4
    val_improves = best_a > 0 and val[best_a]["total_nll"] < val[0.0]["total_nll"] - tol
    test_total_ok = d_total <= tol
    test_exact_ok = d_exact <= tol
    egoals_ok = d_egoals <= 0.03      # expected goals preserved
    keep = bool(val_improves and test_total_ok and test_exact_ok and egoals_ok)

    reasons = [
        f"best validation alpha = {best_a}; validation total-goals NLL "
        f"{val[best_a]['total_nll']:.4f} vs Poisson {val[0.0]['total_nll']:.4f} -> "
        f"{'improves' if val_improves else 'no improvement'}",
        f"TEST total-goals NLL {nb['total_nll']:.4f} vs Poisson {base['total_nll']:.4f} "
        f"(delta {d_total:+.4f}) -> {'OK' if test_total_ok else 'WORSE'}",
        f"TEST exact-score NLL {nb['exact_nll']:.4f} vs Poisson {base['exact_nll']:.4f} "
        f"(delta {d_exact:+.4f}) -> {'OK' if test_exact_ok else 'WORSE'}",
        f"E[goals] preserved: |{nb['e_goals']:.3f} - {base['e_goals']:.3f}| = {d_egoals:.3f} -> "
        f"{'OK' if egoals_ok else 'SHIFTED'}",
        f"over-2.5 calibration (test): pred {base['pred_over']:.3f} vs obs {base['obs_over']:.3f} "
        f"(Poisson), nb pred {nb['pred_over']:.3f}",
    ]
    print("\nGate:")
    for r in reasons:
        print("  - " + r)
    print(f"\n  => {'KEEP over-dispersion a=%s' % best_a if keep else 'DROP (ship Steps 1-3 only)'}")

    _write_report(alphas, val, base, nb, best_a, keep, reasons,
                  str(m.loc[m['played'], 'date'].max().date()))
    return 0


def _write_report(alphas, val, base, nb, best_a, keep, reasons, as_of):
    L = [
        "# Goals-model over-dispersion — GATE result",
        "",
        f"*Generated {datetime.date.today().isoformat()}; data as-of {as_of}. Mean-preserving "
        f"negative-binomial over-dispersion of the Dixon-Coles marginals, reweighted to the same "
        f"W/D/L. Judged on **goal** calibration (total-goals & exact-score NLL) on a time-based "
        f"backtest — NOT 1X2 RPS, which is invariant under W/D/L-preserving reshaping.*",
        "",
        "## Verdict",
        "",
        f"**{'KEEP over-dispersion a=%s.' % best_a if keep else 'DROP — keep the Poisson goals model (negative result).'}**",
        "",
    ]
    L += [f"- {r}" for r in reasons]
    L += ["",
          "Gate: adopt only if the best validation alpha > 0 improves validation total-goals NLL, "
          "AND on the held-out test period both total-goals and exact-score NLL are better or no "
          "worse, AND expected goals are preserved (W/D/L preserved by construction).",
          "",
          f"## Validation grid (period {VAL[1]}..{VAL[2]}, n={val[0.0]['n']})",
          "",
          "| alpha | total-goals NLL | exact-score NLL |",
          "|--:|--:|--:|"]
    for a in alphas:
        star = "  ⭐" if a == best_a else ""
        L.append(f"| {a:.2f} | {val[a]['total_nll']:.4f}{star} | {val[a]['exact_nll']:.4f} |")
    L += ["",
          f"## Held-out test (period {TEST[1]}..{TEST[2]}, n={base['n']})",
          "",
          "| model | total-goals NLL | exact-score NLL | E[goals] | pred P(>2.5) | obs P(>2.5) |",
          "|--|--:|--:|--:|--:|--:|",
          f"| Poisson (a=0) | {base['total_nll']:.4f} | {base['exact_nll']:.4f} | "
          f"{base['e_goals']:.3f} | {base['pred_over']:.3f} | {base['obs_over']:.3f} |",
          f"| NB (a={best_a}) | {nb['total_nll']:.4f} | {nb['exact_nll']:.4f} | "
          f"{nb['e_goals']:.3f} | {nb['pred_over']:.3f} | {nb['obs_over']:.3f} |",
          ""]
    out = ROOT / "reports" / "overdispersion_gate.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nWrote {out}")


_DC_NB: DixonColesModel | None = None

if __name__ == "__main__":
    raise SystemExit(main())
