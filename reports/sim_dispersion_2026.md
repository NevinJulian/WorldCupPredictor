# WC 2026 — sim under-dispersion: diagnosis + strength-uncertainty validation

*Analysis only. Backtest: walk-forward World Cups 2010-2022 (256 matches).*

## Part A — per-match calibration (post-reweight = ensemble H/D/A)

Pooled WC backtest: **RPS 0.2036**, log-loss 0.9837. Best temperature **T\* = 0.79** (min RPS) / **0.87** (min log-loss). `T*>1` would mean over-confident (soften); `T*<1` means **under**-confident.

| Predicted-winner bin | n | mean pred | observed |
|---|--:|--:|--:|
| 0.33-0.45 | 91 | 0.405 | 0.396 |
| 0.45-0.55 | 92 | 0.496 | 0.598 |
| 0.55-0.65 | 41 | 0.590 | 0.659 |
| 0.65-1.01 | 32 | 0.709 | 0.719 |

**Read:** T\* < 1 and the mid bins win more than predicted (e.g. the ~0.50 bin) → the per-match model is **under-confident, not over-confident**. Temperature softening is contraindicated (it would raise RPS).

## Part B — group-advance calibration, baseline vs strength shock
Reconstructed 8 groups × 4 WCs (128 team-tournaments). `rating_sigma` is the per-team rating-shock SD (Elo). The shock is sim-time only, so per-match RPS is unchanged by it.

| rating_sigma | advance Brier | log-loss | favourites P≥0.70 (n) | pred | observed |
|--:|--:|--:|--:|--:|--:|
| 0 (baseline) | 0.1829 | 0.5436 | 27 | 0.800 | 0.889 |
| 30 | 0.1849 | 0.5482 | 27 | 0.796 | 0.889 |
| 60 | 0.1853 | 0.5497 | 27 | 0.788 | 0.889 |
| 100 | 0.1870 | 0.5548 | 21 | 0.794 | 0.857 |

**Read:** baseline favourites *over*-perform (advance ~0.89 vs predicted ~0.80), and the strength shock makes the Brier/log-loss **worse**, not better. The fix fails the keep-criterion on the backtest.

## Part C — the lever's effect on the 2026 title concentration

| rating_sigma | top-2 title mass | top favourite |
|--:|--:|--|
| 0 | 0.456 | Spain 0.243 |
| 60 | 0.436 | Spain 0.234 |
| 120 | 0.389 | Spain 0.211 |

## Verdict

**Neither fix is applied; `rating_sigma` stays 0 (off).** (1) The per-match model is under-confident on the WC backtest (T\* < 1), so temperature softening would hurt RPS. (2) Injecting strength uncertainty does widen the title distribution toward the market (top-2 0.45 → 0.38 at σ=120), but it **worsens** group-advance calibration (Brier 0.1829 → 0.1870) and is RPS-neutral-to-negative — it fails *"keep only if it improves calibration without hurting RPS."* The 47%-vs-market-24% title gap is a genuine model–market disagreement the backtest does **not** resolve against the model. The lever is implemented, tested and documented for if priors change.
