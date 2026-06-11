# Elo hyperparameter tuning

*Generated 2026-06-11; data as-of 2026-06-07. Validation: pooled normalised RPS of the Elo-logistic map over expanding folds 1996-2009 (all end before 2010, never the World Cups). Held-out: the 2010-2022 WC backtest (used only for confirmation).*

## Verdict

**KEEP the eloratings.net defaults (negative result).**

- Default params: `home_adv=100, k_scale=1.0, gd_strength=1.0`
- Best on validation: `home_adv=75.0, k_scale=1.0, gd_strength=1.5` (val RPS 0.1767 vs default 0.1771)

Decision checklist:

- validation RPS 0.1767 vs default 0.1771 -> IMPROVES
- held-out WC RPS (calibrated) 0.2030 vs default 0.2019 -> WORSE
- per-WC calibrated deltas (tuned-default) [0.0024, 0.0002, 0.0045, -0.0027] -> tuned better on 1/4, worse on 3/4 (single-fold-driven)
- confederation gap 0.0425 vs default 0.0433 -> OK

Keep-rule: adopt only if the tuned params improve BOTH the validation RPS AND the held-out WC RPS (or leave it unchanged), the WC gain is not single-fold-driven, and the confederation gap does not worsen.

## Held-out WC backtest (2010-2022)

Bars: Elo-logistic baseline **0.2045**, calibrated ensemble **0.2019**. RPS is the unweighted mean over the four WCs (matching how the 0.2045 bar is quoted).

**Default Elo (home_adv=100, k_scale=1.0, gd_strength=1.0)**

| WC | n | Elo-logistic | Ensemble | Calibrated ens | ens weight |
|--|--:|--:|--:|--:|--:|
| 2010 | 64 | 0.1965 | 0.1954 | 0.1941 | 0.76 |
| 2014 | 64 | 0.1848 | 0.1880 | 0.1844 | 0.83 |
| 2018 | 64 | 0.2104 | 0.2068 | 0.2048 | 0.92 |
| 2022 | 64 | 0.2261 | 0.2241 | 0.2241 | 0.90 |
| **avg** |  | **0.2045** | **0.2036** | **0.2019** |  |
| confed gap |  |  | **0.0433** |  |  |

**Tuned Elo (home_adv=75.0, k_scale=1.0, gd_strength=1.5)**

| WC | n | Elo-logistic | Ensemble | Calibrated ens | ens weight |
|--|--:|--:|--:|--:|--:|
| 2010 | 64 | 0.1968 | 0.1978 | 0.1965 | 0.74 |
| 2014 | 64 | 0.1826 | 0.1884 | 0.1846 | 0.79 |
| 2018 | 64 | 0.2081 | 0.2110 | 0.2093 | 0.92 |
| 2022 | 64 | 0.2267 | 0.2210 | 0.2214 | 0.91 |
| **avg** |  | **0.2036** | **0.2046** | **0.2030** |  |
| confed gap |  |  | **0.0425** |  |  |

## Validation grid (pooled pre-2010 RPS, lower is better)

| home_adv | k_scale | gd_strength | val RPS | n |
|--:|--:|--:|--:|--:|
| 75 | 1.00 | 1.50 | 0.1767  ⭐ | 12807 |
| 100 | 1.00 | 1.50 | 0.1767 | 12807 |
| 50 | 1.00 | 1.50 | 0.1767 | 12807 |
| 100 | 1.50 | 1.50 | 0.1767 | 12807 |
| 125 | 1.50 | 1.50 | 0.1768 | 12807 |
| 75 | 1.50 | 1.50 | 0.1768 | 12807 |
| 125 | 1.00 | 1.50 | 0.1768 | 12807 |
| 50 | 1.50 | 1.50 | 0.1769 | 12807 |
| 100 | 1.50 | 1.00 | 0.1770 | 12807 |
| 75 | 1.50 | 1.00 | 0.1770 | 12807 |
| 125 | 1.50 | 1.00 | 0.1770 | 12807 |
| 50 | 1.50 | 1.00 | 0.1771 | 12807 |
| 75 | 1.00 | 1.00 | 0.1771 | 12807 |
| 50 | 1.00 | 1.00 | 0.1771 | 12807 |
| 100 | 1.00 | 1.00 | 0.1771 | 12807 |
| 125 | 1.00 | 1.00 | 0.1772 | 12807 |
| 75 | 0.75 | 1.50 | 0.1772 | 12807 |
| 50 | 0.75 | 1.50 | 0.1773 | 12807 |
| 100 | 0.75 | 1.50 | 0.1773 | 12807 |
| 125 | 0.75 | 1.50 | 0.1774 | 12807 |
| 75 | 1.50 | 0.50 | 0.1775 | 12807 |
| 100 | 1.50 | 0.50 | 0.1775 | 12807 |
| 50 | 1.50 | 0.50 | 0.1776 | 12807 |
| 125 | 1.50 | 0.50 | 0.1776 | 12807 |
| 50 | 0.75 | 1.00 | 0.1778 | 12807 |
| 75 | 0.75 | 1.00 | 0.1778 | 12807 |
| 75 | 1.00 | 0.50 | 0.1778 | 12807 |
| 50 | 1.00 | 0.50 | 0.1778 | 12807 |
| 100 | 0.75 | 1.00 | 0.1778 | 12807 |
| 100 | 1.00 | 0.50 | 0.1779 | 12807 |
| 125 | 1.00 | 0.50 | 0.1780 | 12807 |
| 125 | 0.75 | 1.00 | 0.1780 | 12807 |
| 50 | 0.75 | 0.50 | 0.1786 | 12807 |
| 75 | 0.75 | 0.50 | 0.1786 | 12807 |
| 100 | 0.75 | 0.50 | 0.1787 | 12807 |
| 125 | 0.75 | 0.50 | 0.1789 | 12807 |
