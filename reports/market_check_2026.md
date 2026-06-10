# WC 2026 — model title odds vs the betting market

*Analysis only (no model change). Odds snapshot: **2026-06-10**, pre-tournament.*

**Method.** De-vig each book: implied = 1/decimal = 100/(american+100), then renormalise the full 48-team field to sum to 1. **Market** = mean of the two sportsbooks' de-vigged probabilities. Sources: **DraftKings** (via ESPN) and **BetMGM** (via Yahoo) — full fields; **Kalshi** (prediction market, via covers.com) shown as a third reference for the top names.

Overrounds before de-vig: DraftKings **1.175**, BetMGM **1.220** (48 teams each).

| Team | Model | Market (DK+MGM) | Gap (pp) | Model/Market | Kalshi |
|------|------:|----------------:|---------:|-------------:|-------:|
| Spain | 24.9% | 15.2% | +9.8 | 1.64 | 17.2% |
| Argentina | 21.8% | 8.4% | +13.5 | 2.61 | 8.7% |
| France | 10.2% | 14.2% | -4.0 | 0.72 | 16.2% |
| England | 7.0% | 10.4% | -3.5 | 0.67 | 10.8% |
| Brazil | 6.1% | 8.6% | -2.5 | 0.71 | 8.4% |
| Colombia | 5.1% | 2.0% | +3.0 | 2.49 | 2.0% |
| Portugal | 3.1% | 8.6% | -5.5 | 0.36 | 10.7% |
| Netherlands | 2.8% | 4.0% | -1.1 | 0.71 | 4.7% |
| Ecuador | 2.7% | 1.0% | +1.7 | 2.65 | — |
| Germany | 2.4% | 5.6% | -3.2 | 0.42 | 5.6% |
| Morocco | 1.9% | 1.8% | +0.1 | 1.05 | 1.7% |
| Belgium | 1.8% | 2.2% | -0.4 | 0.82 | 2.3% |
| Japan | 1.6% | 1.4% | +0.2 | 1.12 | 1.7% |
| Mexico | 1.5% | 1.1% | +0.3 | 1.30 | 1.8% |
| Uruguay | 1.3% | 1.3% | +0.0 | 1.03 | — |

Top-2 concentration: **model 47%** (Spain + Argentina) vs **market 24%**. Top-15 mass: model 0.94 vs market 0.86.

## Read

1. The divergence is **not** uniform favourite-inflation (under-dispersion): the model over-rates
   Spain (x1.6) and the CONMEBOL sides Argentina (x2.6), Colombia (x2.5) and Ecuador (x2.7), while
   *under*-rating the European chasing pack — France, England, Portugal, Germany (x0.4-0.7). So the
   dominant signal is a team/confederation-specific tilt, not a global one.
2. Likely root cause (to investigate, not chase): the in-house Elo + form features over-value
   CONMEBOL teams — long intra-confederation qualifying and Argentina's unbeaten-run rating inflate
   them — and the Elo-heavy ensemble (w_gbm 0.89) compounds it over 7 rounds, concentrating 47% of
   the title in its top two vs the market's 24%. A single unseen injury can't explain a whole-region
   pattern, so this reads as systematic bias, not missing info.
3. There is *also* a mild global under-dispersion (model top-15 mass 0.94 vs market 0.86). Two
   no-code follow-ups worth doing: (a) audit ensemble H/D/A reliability on the backtest, and
   (b) check Elo strength by confederation vs the market. No model change is made here.
