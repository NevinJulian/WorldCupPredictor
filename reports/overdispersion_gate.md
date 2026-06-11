# Goals-model over-dispersion — GATE result

*Generated 2026-06-11; data as-of 2026-06-07. Mean-preserving negative-binomial over-dispersion of the Dixon-Coles marginals, reweighted to the same W/D/L. Judged on **goal** calibration (total-goals & exact-score NLL) on a time-based backtest — NOT 1X2 RPS, which is invariant under W/D/L-preserving reshaping.*

## Verdict

**KEEP over-dispersion a=0.15.**

- best validation alpha = 0.15; validation total-goals NLL 1.9430 vs Poisson 1.9546 -> improves
- TEST total-goals NLL 1.9399 vs Poisson 1.9480 (delta -0.0081) -> OK
- TEST exact-score NLL 2.9320 vs Poisson 2.9613 (delta -0.0292) -> OK
- E[goals] preserved: |2.661 - 2.657| = 0.004 -> OK
- over-2.5 calibration (test): pred 0.485 vs obs 0.495 (Poisson), nb pred 0.471

Gate: adopt only if the best validation alpha > 0 improves validation total-goals NLL, AND on the held-out test period both total-goals and exact-score NLL are better or no worse, AND expected goals are preserved (W/D/L preserved by construction).

## Validation grid (period 2014-01-01..2019-01-01, n=4668)

| alpha | total-goals NLL | exact-score NLL |
|--:|--:|--:|
| 0.00 | 1.9546 | 2.9803 |
| 0.05 | 1.9477 | 2.9631 |
| 0.10 | 1.9441 | 2.9529 |
| 0.15 | 1.9430  ⭐ | 2.9475 |
| 0.20 | 1.9436 | 2.9453 |
| 0.30 | 1.9481 | 2.9479 |

## Held-out test (period 2019-01-01..2027-01-01, n=7147)

| model | total-goals NLL | exact-score NLL | E[goals] | pred P(>2.5) | obs P(>2.5) |
|--|--:|--:|--:|--:|--:|
| Poisson (a=0) | 1.9480 | 2.9613 | 2.657 | 0.485 | 0.495 |
| NB (a=0.15) | 1.9399 | 2.9320 | 2.661 | 0.471 | 0.495 |
