# In-tournament xG adjustment — GATE result

*Generated 2026-06-13; data as-of 2026-06-07. Backtest on the 2018 & 2022 World Cups (StatsBomb open-data xG). For each WC: a fixed Elo->1X2 map fit on pre-tournament data, then the tournament walked in date order updating ratings from the real scoreline (result-only) vs the xG-adjusted effective scoreline. Later matches (both teams with >=1 prior game) scored with normalized RPS, pooled across both WCs (n=96). As-of / leakage-free; lightly validated (2 tournaments).*

## Verdict

**KEEP the xG adjustment ON by default with conservative balanced defaults (lam=0.5, shrink=0.75).**

- best xG-adjusted config: lam=0.0, shrink=0.75 -> RPS 0.2160 vs result-only 0.2195 (delta -0.0035) -> IMPROVES/NEUTRAL (gate tol 0.001)
- paired bootstrap (best vs result-only, n=96): mean gap +0.0035, 95% CI [-0.0048, +0.0121] -> NOT significant (small n; CI spans 0)
- shipped default lam=0.5, shrink=0.75 (conservative, balanced goal/xG trust) -> RPS 0.2179 (delta -0.0015); chosen over the aggressive pure-xG optimum given the small-sample insignificance
- Lightly validated: 2 tournaments, 96 later matches. xG is the only lever (possession/shots not weighted).

Gate: adopt ON only if the best (lam, shrink) improves or is neutral (delta <= 0.001) on the pooled later-match RPS vs result-only. Either way the lever ships via `xg_adjust` knobs (`XG_LAMBDA`, `XG_SHRINK`) and `build_forecast_model(xg_adjustment=...)`.

## Result-only baseline: RPS **0.2195** (pooled later matches, n=96)

## xG-adjusted sweep (lam = weight on goals, shrink = adjustment strength)

| lam | shrink | RPS | delta vs result-only | scorelines adjusted |
|--:|--:|--:|--:|--:|
| 0.00 | 0.75 | 0.2160  ⭐ | -0.0035 | 125 |
| 0.25 | 1.00 | 0.2160 | -0.0035 | 125 |
| 0.00 | 0.50 | 0.2177 | -0.0018 | 125 |
| 0.50 | 1.00 | 0.2177 | -0.0018 | 125 |
| 0.25 | 0.50 | 0.2179 | -0.0015 | 125 |
| 0.50 | 0.75 | 0.2179 | -0.0015 | 125 |
| 0.00 | 1.00 | 0.2181 | -0.0014 | 125 |
| 0.25 | 0.75 | 0.2188 | -0.0007 | 125 |
| 0.25 | 0.25 | 0.2192 | -0.0003 | 125 |
| 0.75 | 0.75 | 0.2192 | -0.0003 | 125 |
| 0.75 | 0.25 | 0.2195 | +0.0000 | 125 |
| 0.50 | 0.25 | 0.2195 | +0.0000 | 125 |
| 0.75 | 0.50 | 0.2195 | +0.0000 | 125 |
| 0.00 | 0.25 | 0.2210 | +0.0015 | 125 |
| 0.50 | 0.50 | 0.2210 | +0.0015 | 125 |
| 0.75 | 1.00 | 0.2210 | +0.0015 | 125 |

*lam = 1 or shrink = 0 reduces exactly to result-only. xG is the only lever; possession / shots are intentionally not weighted into the update.*
