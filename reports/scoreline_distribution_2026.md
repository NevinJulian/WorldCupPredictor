# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-17; generated 2026-06-19. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Czechia | South Africa | 1.31 | 0.80 | **1-0** | 1-0 (18%), 0-0 (14%), 1-1 (11%) | 50/27/22 |
| Mexico | South Korea | 1.74 | 0.93 | **1-0** | 1-0 (13%), 1-1 (11%), 0-0 (10%) | 55/26/18 |
| Mexico | Czechia | 2.00 | 0.85 | **1-0** | 1-0 (11%), 1-1 (11%), 2-0 (10%) | 61/26/13 |
| South Africa | South Korea | 0.66 | 1.45 | **0-1** | 0-1 (20%), 0-0 (13%), 0-2 (12%) | 17/25/58 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Switzerland | Bosnia and Herzegovina | 1.78 | 0.67 | **1-0** | 1-0 (16%), 2-0 (12%), 0-0 (12%) | 63/26/11 |
| Canada | Qatar | 2.33 | 0.78 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (10%) | 74/16/10 |
| Canada | Switzerland | 1.32 | 1.31 | **1-1** | 1-1 (12%), 0-0 (10%), 0-1 (10%) | 34/29/37 |
| Bosnia and Herzegovina | Qatar | 1.35 | 0.98 | **1-0** | 1-0 (14%), 0-0 (13%), 1-1 (12%) | 46/30/24 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Morocco | 0.70 | 1.29 | **0-1** | 0-1 (16%), 0-0 (16%), 1-1 (11%) | 22/29/49 |
| Brazil | Haiti | 2.71 | 0.64 | **2-0** | 2-0 (12%), 1-0 (11%), 3-0 (10%) | 78/16/6 |
| Scotland | Brazil | 0.67 | 1.93 | **0-0** | 0-0 (12%), 0-1 (12%), 0-2 (11%) | 12/28/60 |
| Morocco | Haiti | 1.95 | 0.58 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 72/19/8 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Australia | 1.36 | 1.30 | **1-1** | 1-1 (12%), 0-0 (10%), 0-1 (9%) | 36/29/35 |
| Türkiye | Paraguay | 1.19 | 1.01 | **0-0** | 0-0 (14%), 1-0 (13%), 1-1 (12%) | 40/30/30 |
| United States | Türkiye | 1.69 | 1.28 | **1-1** | 1-1 (12%), 0-0 (8%), 0-1 (7%) | 42/27/31 |
| Paraguay | Australia | 0.82 | 1.27 | **0-1** | 0-1 (16%), 0-0 (14%), 1-1 (11%) | 25/28/47 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Ivory Coast | 1.84 | 0.89 | **1-0** | 1-0 (14%), 2-0 (11%), 2-1 (10%) | 62/21/17 |
| Ecuador | Curaçao | 2.10 | 0.54 | **1-0** | 1-0 (18%), 2-0 (15%), 3-0 (9%) | 76/17/7 |
| Curaçao | Ivory Coast | 0.68 | 1.97 | **0-1** | 0-1 (15%), 0-2 (13%), 0-0 (9%) | 11/22/67 |
| Ecuador | Germany | 1.11 | 1.29 | **1-1** | 1-1 (12%), 0-0 (12%), 0-1 (10%) | 33/29/38 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Sweden | 1.78 | 1.01 | **1-0** | 1-0 (11%), 1-1 (10%), 2-0 (9%) | 55/23/22 |
| Tunisia | Japan | 0.64 | 1.67 | **0-1** | 0-1 (18%), 0-0 (13%), 0-2 (13%) | 10/28/62 |
| Japan | Sweden | 1.69 | 0.94 | **1-0** | 1-0 (12%), 1-1 (12%), 0-0 (10%) | 53/28/19 |
| Tunisia | Netherlands | 0.64 | 1.80 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (11%) | 8/26/66 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Iran | 1.51 | 1.00 | **1-0** | 1-0 (15%), 1-1 (10%), 2-0 (10%) | 52/23/25 |
| New Zealand | Egypt | 0.72 | 1.47 | **0-1** | 0-1 (19%), 0-0 (13%), 0-2 (11%) | 15/27/58 |
| Egypt | Iran | 0.92 | 1.13 | **0-0** | 0-0 (14%), 0-1 (14%), 1-0 (13%) | 32/28/40 |
| New Zealand | Belgium | 0.77 | 1.94 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (11%) | 9/29/62 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Saudi Arabia | 2.23 | 0.48 | **1-0** | 1-0 (18%), 2-0 (16%), 3-0 (10%) | 80/17/4 |
| Uruguay | Cape Verde | 1.73 | 0.50 | **1-0** | 1-0 (21%), 2-0 (15%), 0-0 (12%) | 69/22/10 |
| Cape Verde | Saudi Arabia | 0.84 | 1.10 | **0-1** | 0-1 (16%), 0-0 (16%), 1-0 (12%) | 29/30/42 |
| Uruguay | Spain | 0.77 | 1.50 | **0-1** | 0-1 (16%), 0-0 (13%), 1-1 (11%) | 18/28/54 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Iraq | 2.02 | 0.47 | **1-0** | 1-0 (21%), 2-0 (16%), 2-1 (10%) | 78/18/4 |
| Norway | Senegal | 1.29 | 1.01 | **1-0** | 1-0 (15%), 0-0 (12%), 1-1 (11%) | 46/26/28 |
| Norway | France | 0.88 | 1.63 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (11%) | 20/27/53 |
| Senegal | Iraq | 1.42 | 0.64 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 57/27/16 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Austria | 1.94 | 0.60 | **1-0** | 1-0 (16%), 2-0 (14%), 0-0 (10%) | 68/23/9 |
| Jordan | Algeria | 0.92 | 1.64 | **1-1** | 1-1 (12%), 0-1 (12%), 0-0 (11%) | 21/28/51 |
| Algeria | Austria | 1.15 | 1.32 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (11%) | 29/28/42 |
| Jordan | Argentina | 0.51 | 2.19 | **0-1** | 0-1 (14%), 0-2 (14%), 0-0 (11%) | 4/25/71 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | Uzbekistan | 1.69 | 0.66 | **1-0** | 1-0 (16%), 0-0 (13%), 2-0 (12%) | 60/29/12 |
| Colombia | DR Congo | 1.76 | 0.51 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (12%) | 69/23/9 |
| Colombia | Portugal | 1.24 | 1.05 | **1-0** | 1-0 (13%), 0-0 (13%), 1-1 (12%) | 41/29/30 |
| DR Congo | Uzbekistan | 0.92 | 1.01 | **0-0** | 0-0 (16%), 1-0 (14%), 0-1 (14%) | 34/30/37 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Ghana | 2.00 | 0.47 | **1-0** | 1-0 (20%), 2-0 (16%), 0-0 (10%) | 76/19/5 |
| Panama | Croatia | 0.86 | 1.61 | **0-1** | 0-1 (14%), 0-0 (11%), 1-1 (11%) | 20/27/54 |
| Panama | England | 0.57 | 1.94 | **0-1** | 0-1 (16%), 0-2 (13%), 0-0 (12%) | 6/27/67 |
| Croatia | Ghana | 1.66 | 0.67 | **1-0** | 1-0 (18%), 2-0 (12%), 0-0 (12%) | 62/27/12 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: France** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, B, D, E, G, I, J, K

**R32**  
- Ecuador 1-0 Türkiye → **Ecuador** (48% / 27% to win)
- France 1-0 Iran → **France** (59% / 14% to win)
- South Korea 0-1 Switzerland → **Switzerland** (25% / 44% to win)
- Netherlands 0-0 Morocco → **Netherlands** (37% / 33% to win)
- Brazil 1-1 Japan → **Brazil** (48% / 22% to win)
- Germany 1-0 Senegal → **Germany** (55% / 24% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (48% / 25% to win)
- England 1-0 Uzbekistan → **England** (68% / 9% to win)
- Portugal 1-1 Croatia → **Portugal** (46% / 25% to win)
- Spain 1-0 Algeria → **Spain** (67% / 10% to win)
- Australia 1-0 Bosnia and Herzegovina → **Australia** (68% / 11% to win)
- Belgium 1-0 Czechia → **Belgium** (61% / 14% to win)
- Argentina 1-0 Uruguay → **Argentina** (51% / 20% to win)
- United States 0-0 Egypt → **Egypt** (34% / 36% to win)
- Canada 0-1 Austria → **Austria** (31% / 41% to win)
- Colombia 1-0 Norway → **Colombia** (50% / 24% to win)

**R16**  
- Ecuador 0-1 France → **France** (30% / 46% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (27% / 45% to win)
- Brazil 1-1 Germany → **Brazil** (44% / 28% to win)
- Mexico 0-1 England → **England** (20% / 51% to win)
- Portugal 0-1 Spain → **Spain** (19% / 52% to win)
- Australia 1-1 Belgium → **Belgium** (23% / 45% to win)
- Argentina 1-0 Egypt → **Argentina** (64% / 8% to win)
- Austria 0-1 Colombia → **Colombia** (24% / 53% to win)

**QF**  
- France 1-0 Netherlands → **France** (47% / 29% to win)
- Brazil 0-0 England → **England** (32% / 38% to win)
- Spain 1-0 Belgium → **Spain** (55% / 19% to win)
- Argentina 1-0 Colombia → **Argentina** (51% / 22% to win)

**SF**  
- France 0-0 England → **England** (36% / 36% to win)
- Spain 0-0 Argentina → **Argentina** (35% / 35% to win)

**Final**  
- England 0-1 Argentina → **Argentina** (24% / 47% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): C, E, K, J, F, I, A, D

**R32**  
- Ivory Coast 2-3 Türkiye → **Türkiye**
- France 2-0 Tunisia → **France**
- South Korea 1-1 Canada → **South Korea** *(pens)*
- Sweden 2-1 Scotland → **Sweden**
- Brazil 0-0 Netherlands → **Brazil** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 3-1 Morocco → **Mexico**
- England 1-4 Colombia → **Colombia**
- DR Congo 1-0 Panama → **DR Congo**
- Spain 2-0 Austria → **Spain**
- Paraguay 2-0 Ecuador → **Paraguay**
- Belgium 1-1 Czechia → **Belgium** *(pens)*
- Argentina 2-0 Uruguay → **Argentina**
- Australia 1-0 Egypt → **Australia**
- Switzerland 1-2 Algeria → **Algeria**
- Portugal 2-1 Senegal → **Portugal**

**R16**  
- Türkiye 2-4 France → **France**
- South Korea 0-1 Sweden → **Sweden**
- Brazil 4-1 Germany → **Brazil**
- Mexico 0-0 Colombia → **Colombia** *(pens)*
- DR Congo 1-3 Spain → **Spain**
- Paraguay 0-0 Belgium → **Belgium** *(pens)*
- Argentina 3-0 Australia → **Argentina**
- Algeria 0-0 Portugal → **Portugal** *(pens)*

**QF**  
- France 3-1 Sweden → **France**
- Brazil 1-1 Colombia → **Colombia** *(pens)*
- Spain 1-0 Belgium → **Spain**
- Argentina 0-2 Portugal → **Portugal**

**SF**  
- France 1-0 Colombia → **France**
- Spain 0-2 Portugal → **Portugal**

**Final**  
- France 1-0 Portugal → **France**

**Sampled-scenario champion: France** 🏆
