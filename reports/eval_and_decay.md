# Broadened evaluation + Dixon-Coles half-life sweep

*Generated 2026-06-12; data as-of 2026-06-07. Expanding-window, as-of block backtest: refit at yearly checkpoints over 2004-2025, each block predicted only from prior matches. Metric (a) = competitive internationals (qualifiers + continental + WC finals), (b) = all incl. friendlies, (c) = the WC-finals walk-forward (bare DC and the shipped calibrated ensemble). Normalized RPS, lower better.*

## Verdict

**ADOPT a 5y (1825-day) Dixon-Coles strength half-life — was 1.5y / 547d.**

- (a) competitive RPS at adopted 5y (0.1638) vs current 1.5y (0.1737); paired-bootstrap mean gap +0.0100 (95% CI [+0.0089, +0.0110]) -> clearly better
- (a) plateau floor is 10y (0.1632); the marginal gain past 5y is 0.0006 RPS -> negligible, so 5y is taken as the operating point over the longer floor
- (c) bare-DC WC RPS 0.2128 vs current 0.2147 -> OK; product (calibrated-ensemble) WC RPS 0.2025 vs current 0.2019 -> OK (flat within WC-finals noise)
- competitive calibration error 0.0364 vs current 0.0511 -> OK (improved)
- => ADOPT 5y

Gate: adopt a new half-life only if it improves competitive RPS (a) by a margin whose paired-bootstrap 95% CI excludes zero, AND does not raise either WC RPS (c) by more than 0.001, AND does not worsen competitive calibration by more than 0.002. The operating point is the moderate value capturing most of the (a) gain, not the longer plateau floor.

## Sweep

| half-life | (a) competitive | (b) all | friendlies | (c) DC · WC | (c) product · WC | comp. ECE |
|--|--:|--:|--:|--:|--:|--:|
| 1y | 0.1802 | 0.1905 | 0.1987 | 0.2150 | 0.2017 | 0.0527 |
| 1.5y **was current** | 0.1737 | 0.1850 | 0.1954 | 0.2147 | 0.2019 | 0.0511 |
| 2y | 0.1700 | 0.1818 | 0.1933 | 0.2145 | 0.2022 | 0.0492 |
| 3y | 0.1663 | 0.1785 | 0.1910 | 0.2141 | 0.2025 | 0.0428 |
| 4y | 0.1646 | 0.1770 | 0.1897 | 0.2135 | 0.2026 | 0.0393 |
| 5y **ADOPTED** | 0.1638 | 0.1763 | 0.1890 | 0.2128 | 0.2025 | 0.0364 |
| 7y | 0.1632 | 0.1757 | 0.1884 | 0.2115 | 0.2023 | 0.0311 |
| 10y **(a) floor** | 0.1632 | 0.1758 | 0.1883 | 0.2100 | 0.2019 | 0.0270 |

Competitive-match counts: n(a) = 10,320, n(all) = 21,244 (vs ~256 WC-finals matches — the point of the broader detector).

## Reading

- The adopted competitive-match RPS (~0.164, down from ~0.174) sits near the Ley et al. (2019) national-team reference of ~0.165; the residual gap reflects our 1872-onward, all-confederation sample (theirs is a tighter modern, mostly-European slice).
- Metric (c) is unchanged as the relevance bar: bare DC ~0.215, the shipped calibrated ensemble ~0.202. The half-life only reweights the DC fit, so (c) is the guard that a more-reactive or more-stable DC does not cost the product on the tournament that matters.
- Paired bootstrap (best vs current, competitive, n_boot=5000): mean gap +0.0100, 95% CI [+0.0089, +0.0110].
