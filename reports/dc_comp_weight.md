# Dixon-Coles competition-weight sweep (down-weight friendlies)

*Generated 2026-06-27; data as-of 2026-06-14. Expanding-window, as-of block backtest: refit at yearly checkpoints over 2004-2025, each block predicted only from prior matches. Metric (a) = competitive internationals (qualifiers + continental + WC finals), (b) = all incl. friendlies, (c) = the WC-finals walk-forward (bare DC and the shipped calibrated ensemble). Normalized RPS, lower better. The friendly weight scales friendlies in the DC likelihood; competitive/other stay 1.0.*

## Verdict

**KEEP recency-only (friendly weight 1.0) — negative result.**

- lowest competitive RPS is at the current weight 1.0 (0.1638) — down-weighting friendlies does not help (a)
- => KEEP friendly weight 1.0 (negative result)

Gate: adopt a non-1.0 friendly weight only if it improves competitive RPS (a) by a margin whose paired-bootstrap 95% CI excludes zero, AND does not raise either WC RPS (c) by more than 0.001, AND does not worsen competitive calibration by more than 0.002. The parameter ships either way (backward-compatible, off by default).

## Sweep

| friendly weight | (a) competitive | (b) all | friendlies | (c) DC · WC | (c) product · WC | comp. ECE |
|--|--:|--:|--:|--:|--:|--:|
| 1.0 **current, (a) floor** | 0.1638 | 0.1763 | 0.1890 | 0.2128 | 0.2034 | 0.0364 |
| 0.75 | 0.1640 | 0.1768 | 0.1901 | 0.2154 | 0.2037 | 0.0359 |
| 0.5 | 0.1644 | 0.1776 | 0.1919 | 0.2195 | 0.2040 | 0.0351 |
| 0.3 | 0.1648 | 0.1786 | 0.1940 | 0.2246 | 0.2044 | 0.0347 |
| 0.1 | 0.1655 | 0.1802 | 0.1976 | 0.2334 | 0.2047 | 0.0326 |

Competitive-match counts: n(a) = 10,320, n(all) = 21,245 (vs ~256 WC-finals matches — the point of the broader detector). Friendlies are 10,925+ of the all-internationals pool.

## Reading

- Metric (a) is the sensitive detector; the friendly weight is meant to sharpen it by leaning the goals fit on competitive matches. Metric (c) is the relevance guard — the friendly weight only reweights the DC fit, so (c) confirms a friendly-leaner DC does not cost the product on the tournament that matters (bare DC ~0.215, shipped ensemble ~0.202).
- **Why it washes out:** down-weighting friendlies monotonically *worsens* competitive RPS (a) and clearly worsens both WC RPS metrics (c), buying only a small calibration (ECE) gain. This model deliberately trains on every international since 1872 because friendlies carry real strength signal — for sparse / younger national sides they are often the bulk of recent form — so discounting them discards information the goals fit relies on. The blueprint's friendly-discount helps models trained on a narrower modern slice; it does not transfer here. The parameter still ships (off by default) for future use — a different tier, or a smaller-sample regime where friendly noise dominates.
