# WC 2026 — confederation calibration

*Analysis. Walk-forward World Cups 2010-2022; the per-confederation offset is fit on each fold's pre-tournament training set only (leakage-safe).*

## Overall RPS (lower is better)

| WC | n | base | calibrated |
|--|--:|--:|--:|
| 2010 | 64 | 0.1954 | 0.1941 |
| 2014 | 64 | 0.1880 | 0.1844 |
| 2018 | 64 | 0.2068 | 0.2048 |
| 2022 | 64 | 0.2241 | 0.2241 |
| **pooled** | 256 | **0.2036** | **0.2019** |

Elo bar = 0.2045. The calibration moves the ensemble **0.2036 -> 0.2019** (vs the bar 0.2045).

## Per-confederation predicted-vs-actual gap (inter-confederation WC matches)
Gap = (predicted − actual) expected points/game; **> 0 = over-predicted**. Closer to 0 is better.

| Confed | n | gap base | gap calibrated |
|--|--:|--:|--:|
| UEFA | 151 | -0.123 | -0.080 |
| CONMEBOL | 87 | -0.110 | -0.065 |
| CAF | 72 | +0.051 | +0.023 |
| AFC | 63 | +0.133 | +0.069 |
| CONCACAF | 50 | +0.193 | +0.113 |

Mean |gap| across the five confederations: **0.122 -> 0.070**. The AFC / CONCACAF over-prediction shrinks and CONMEBOL / UEFA under-prediction eases.

## Verdict

**KEEP — on by default.** It improves overall RPS (0.2036 -> 0.2019, below the 0.2045 bar) **and** narrows every confederation's gap — it does not trade RPS to chase the gap. The offset applied to the 2026 forecast (fit on all played data):

| Confed | UEFA | CONMEBOL | CAF | AFC | CONCACAF |
|--|--:|--:|--:|--:|--:|
| offset | +0.043 | +0.042 | +0.026 | +0.006 | -0.003 |

The effect on the 2026 title odds is small (a deliberately small offset); the win is the backtest RPS + calibration. Estimated leakage-safe per fold (only pre-WC matches).
