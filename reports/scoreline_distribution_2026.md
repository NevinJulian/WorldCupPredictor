# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-23; generated 2026-06-24. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | Czechia | 1.97 | 0.87 | **1-1** | 1-1 (11%), 1-0 (11%), 2-0 (10%) | 59/26/14 |
| South Africa | South Korea | 0.68 | 1.37 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (11%) | 18/28/54 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Switzerland | 1.38 | 1.30 | **1-1** | 1-1 (12%), 0-0 (10%), 0-1 (9%) | 36/29/35 |
| Bosnia and Herzegovina | Qatar | 1.33 | 1.09 | **1-0** | 1-0 (13%), 1-1 (11%), 0-0 (11%) | 44/26/30 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Brazil | 0.68 | 1.92 | **0-1** | 0-1 (12%), 0-0 (12%), 0-2 (11%) | 14/26/60 |
| Morocco | Haiti | 1.95 | 0.55 | **1-0** | 1-0 (19%), 2-0 (15%), 0-0 (10%) | 72/22/6 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Türkiye | 1.80 | 1.16 | **1-1** | 1-1 (12%), 0-0 (9%), 1-0 (8%) | 48/28/24 |
| Paraguay | Australia | 0.90 | 1.16 | **0-1** | 0-1 (14%), 0-0 (14%), 1-0 (13%) | 31/27/42 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Curaçao | Ivory Coast | 0.70 | 1.87 | **0-1** | 0-1 (14%), 0-2 (12%), 0-0 (11%) | 12/25/63 |
| Ecuador | Germany | 1.13 | 1.27 | **1-1** | 1-1 (11%), 0-0 (11%), 1-0 (11%) | 35/27/38 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Japan | Sweden | 1.76 | 0.97 | **1-0** | 1-0 (12%), 1-1 (10%), 2-0 (10%) | 56/23/21 |
| Tunisia | Netherlands | 0.66 | 1.85 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (10%) | 10/23/67 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Egypt | Iran | 0.92 | 1.08 | **0-0** | 0-0 (16%), 0-1 (13%), 1-0 (13%) | 32/31/37 |
| New Zealand | Belgium | 0.76 | 2.01 | **0-1** | 0-1 (13%), 0-2 (11%), 1-1 (11%) | 9/26/65 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Cape Verde | Saudi Arabia | 0.90 | 1.11 | **0-1** | 0-1 (16%), 0-0 (14%), 1-0 (13%) | 32/26/42 |
| Uruguay | Spain | 0.77 | 1.49 | **0-1** | 0-1 (15%), 0-0 (14%), 1-1 (12%) | 17/31/53 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Norway | France | 0.89 | 1.65 | **0-1** | 0-1 (13%), 1-1 (11%), 0-0 (11%) | 20/27/53 |
| Senegal | Iraq | 1.38 | 0.69 | **1-0** | 1-0 (18%), 0-0 (15%), 2-0 (11%) | 53/28/19 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Algeria | Austria | 1.14 | 1.31 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (11%) | 29/29/42 |
| Jordan | Argentina | 0.49 | 2.31 | **0-1** | 0-1 (15%), 0-2 (15%), 0-3 (10%) | 4/20/76 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Colombia | Portugal | 1.18 | 1.12 | **0-0** | 0-0 (13%), 1-0 (12%), 1-1 (12%) | 38/29/34 |
| DR Congo | Uzbekistan | 0.82 | 1.12 | **0-1** | 0-1 (17%), 0-0 (16%), 1-1 (11%) | 27/30/43 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Panama | England | 0.62 | 1.84 | **0-1** | 0-1 (15%), 0-2 (13%), 0-0 (12%) | 11/26/63 |
| Croatia | Ghana | 1.66 | 0.68 | **1-0** | 1-0 (19%), 2-0 (13%), 0-0 (11%) | 63/23/14 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: England** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): B, D, E, F, G, H, J, K

**R32**  
- Ivory Coast 0-1 Paraguay → **Paraguay** (32% / 44% to win)
- Senegal 0-1 Sweden → **Senegal** (40% / 37% to win)
- South Korea 0-1 Canada → **Canada** (33% / 41% to win)
- Netherlands 1-1 Brazil → **Brazil** (31% / 43% to win)
- Morocco 1-0 Japan → **Morocco** (44% / 28% to win)
- Germany 1-1 France → **France** (28% / 45% to win)
- Mexico 1-0 Cape Verde → **Mexico** (65% / 10% to win)
- England 1-0 Portugal → **England** (42% / 30% to win)
- Colombia 1-0 Croatia → **Colombia** (50% / 21% to win)
- Spain 1-0 Austria → **Spain** (62% / 14% to win)
- United States 0-1 Switzerland → **Switzerland** (26% / 45% to win)
- Belgium 1-0 Algeria → **Belgium** (53% / 26% to win)
- Argentina 1-0 Saudi Arabia → **Argentina** (75% / 4% to win)
- Australia 0-0 Iran → **Australia** (37% / 34% to win)
- Bosnia and Herzegovina 0-1 Egypt → **Egypt** (16% / 57% to win)
- Uzbekistan 0-1 Ecuador → **Ecuador** (17% / 53% to win)

**R16**  
- Paraguay 1-0 Senegal → **Paraguay** (37% / 33% to win)
- Canada 0-1 Brazil → **Brazil** (15% / 57% to win)
- Morocco 0-1 France → **France** (26% / 46% to win)
- Mexico 0-1 England → **England** (21% / 49% to win)
- Colombia 0-1 Spain → **Spain** (20% / 50% to win)
- Switzerland 1-1 Belgium → **Belgium** (34% / 37% to win)
- Argentina 1-0 Australia → **Argentina** (67% / 11% to win)
- Egypt 0-1 Ecuador → **Ecuador** (25% / 47% to win)

**QF**  
- Paraguay 0-0 Brazil → **Brazil** (14% / 56% to win)
- France 1-0 England → **France** (39% / 35% to win)
- Spain 1-1 Belgium → **Spain** (48% / 26% to win)
- Argentina 1-0 Ecuador → **Argentina** (60% / 14% to win)

**SF**  
- Brazil 0-1 France → **France** (36% / 40% to win)
- Spain 0-0 Argentina → **Argentina** (24% / 40% to win)

**Final**  
- France 0-1 Argentina → **Argentina** (27% / 47% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): F, E, D, L, B, H, J, K

**R32**  
- Ivory Coast 2-2 Australia → **Australia** *(pens)*
- France 1-2 Netherlands → **Netherlands**
- South Korea 1-0 Bosnia and Herzegovina → **South Korea**
- Japan 2-0 Morocco → **Japan**
- Brazil 0-0 Sweden → **Brazil** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 3-3 Ecuador → **Ecuador** *(pens)*
- England 1-1 Uzbekistan → **England** *(pens)*
- Colombia 3-1 Croatia → **Colombia**
- Uruguay 1-0 Austria → **Uruguay**
- Paraguay 1-1 Canada → **Canada** *(pens)*
- Belgium 1-1 Saudi Arabia → **Belgium** *(pens)*
- Argentina 2-1 Spain → **Argentina**
- United States 3-0 Egypt → **United States**
- Switzerland 0-1 Algeria → **Algeria**
- Portugal 5-0 Panama → **Portugal**

**R16**  
- Australia 0-0 Netherlands → **Netherlands** *(pens)*
- South Korea 2-1 Japan → **South Korea**
- Brazil 0-2 Germany → **Germany**
- Ecuador 0-2 England → **England**
- Colombia 2-1 Uruguay → **Colombia**
- Canada 0-0 Belgium → **Belgium** *(pens)*
- Argentina 3-1 United States → **Argentina**
- Algeria 1-1 Portugal → **Portugal** *(pens)*

**QF**  
- Netherlands 1-0 South Korea → **Netherlands**
- Germany 0-1 England → **England**
- Colombia 1-0 Belgium → **Colombia**
- Argentina 0-2 Portugal → **Portugal**

**SF**  
- Netherlands 0-3 England → **England**
- Colombia 3-3 Portugal → **Portugal** *(pens)*

**Final**  
- England 1-0 Portugal → **England**

**Sampled-scenario champion: England** 🏆
