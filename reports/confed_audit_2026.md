# WC 2026 — confederation-bias audit (is the model over-rating CONMEBOL?)

*Analysis only (no model change). Backtest: walk-forward World Cups 2010-2022.*

## Part 1 — per-match calibration (inter-confederation WC matches)
Predicted vs actual **expected points per game** (3·win + 1·draw), each side bucketed by its confederation. `~1SE` is a rough one-sigma band on the actual rate.

| Confed | n | Elo-base pred | Ensemble pred | Actual | Ensemble gap | ~1SE |
|--------|--:|--------------:|--------------:|-------:|-------------:|-----:|
| UEFA | 151 | 1.63 | 1.57 | 1.69 | -0.12 | 0.12 |
| CONMEBOL | 87 | 1.80 | 1.71 | 1.82 | -0.11 | 0.16 |
| CAF | 72 | 0.93 | 1.01 | 0.96 | +0.05 | 0.18 |
| AFC | 63 | 1.00 | 1.02 | 0.89 | +0.13 | 0.19 |
| CONCACAF | 50 | 1.14 | 1.17 | 0.98 | +0.19 | 0.21 |
| OFC | 3 | 0.97 | 1.02 | 1.00 | +0.02 | 0.87 |

*(gap > 0 = model over-predicts that confederation; gap < 0 = under-predicts.)*

## Part 2 — Elo drift, CONMEBOL vs UEFA
**(a) Mean pre-WC Elo of World Cup participants:**

| Year | CONMEBOL | UEFA | Gap | n (CON/UEFA) |
|------|---------:|-----:|----:|:------------:|
| 2010 | 1936 | 1887 | +49 | 5/13 |
| 2014 | 2006 | 1940 | +65 | 6/13 |
| 2018 | 2036 | 1932 | +104 | 5/14 |
| 2022 | 2085 | 1994 | +91 | 4/13 |

**(b) CONMEBOL-vs-UEFA head-to-head win-share (win=1, draw=0.5, loss=0) vs the Elo-implied win probability:**

| Era | n | Actual | Elo-implied | Actual − Elo |
|-----|--:|-------:|------------:|-------------:|
| 1990-2009 | 320 | 0.539 | 0.551 | -0.012 |
| 2010-2017 | 138 | 0.572 | 0.582 | -0.010 |
| 2018-2026 | 81 | 0.549 | 0.585 | -0.036 |

## Read

**Verdict: defensible disagreement with the market — keep it (monitor, don't fix).**

1. **No backtested CONMEBOL over-rating — the opposite.** On the 2010-2022 WC backtest the model
   slightly *under*-predicts CONMEBOL (actual 1.82 expected-points/game vs 1.71-1.80 predicted)
   and UEFA (1.69 vs 1.57-1.63) in inter-confederation matches. The only buckets it over-predicts
   are the weaker AFC (+0.13) and CONCACAF (+0.19) — opposite to the market narrative. The
   Elo-logistic baseline shows the same shape, so it is an Elo-rating effect, not a GBM artifact.
2. **Elo isn't drifting high enough to matter.** CONMEBOL's mean-Elo edge over UEFA among WC teams
   grew (+49 in 2010 to +91 in 2022), but the CONMEBOL-vs-UEFA head-to-head only under-delivers the
   Elo expectation by ~1pp (1990-2017), widening to ~3.6pp win-share in 2018-2026 — within sampling
   noise (n=81). A mild recent drift to watch, not a measurable bias.
3. **So the model's CONMEBOL/Spain confidence is earned at World Cups; the market is just more
   bearish** (host conditions, squad age, risk premia it prices that the model can't see). The
   title-level over-concentration vs the market (top-2 47% vs 24%) is better explained by iid-sim
   under-dispersion — and possibly intra-bucket top-team concentration (e.g. Argentina, which a
   confederation average can't isolate) — than by a confederation rating bias. No fix warranted.
