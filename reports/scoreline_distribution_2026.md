# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-21; generated 2026-06-23. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | Czechia | 1.99 | 0.85 | **1-1** | 1-1 (12%), 1-0 (11%), 2-0 (10%) | 60/27/13 |
| South Africa | South Korea | 0.69 | 1.36 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (11%) | 19/28/53 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Switzerland | 1.45 | 1.22 | **1-1** | 1-1 (13%), 0-0 (10%), 1-0 (9%) | 40/30/31 |
| Bosnia and Herzegovina | Qatar | 1.32 | 1.12 | **1-0** | 1-0 (13%), 1-1 (10%), 0-0 (10%) | 44/24/32 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Brazil | 0.67 | 1.94 | **0-1** | 0-1 (12%), 0-2 (12%), 0-0 (12%) | 14/25/61 |
| Morocco | Haiti | 1.94 | 0.58 | **1-0** | 1-0 (18%), 2-0 (15%), 2-1 (9%) | 72/20/8 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Türkiye | 1.82 | 1.14 | **1-1** | 1-1 (12%), 0-0 (9%), 1-0 (8%) | 48/28/23 |
| Paraguay | Australia | 0.90 | 1.15 | **0-0** | 0-0 (15%), 0-1 (14%), 1-0 (13%) | 31/28/41 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Curaçao | Ivory Coast | 0.73 | 1.81 | **0-1** | 0-1 (14%), 0-2 (12%), 0-0 (11%) | 14/25/60 |
| Ecuador | Germany | 1.15 | 1.24 | **1-1** | 1-1 (12%), 0-0 (12%), 1-0 (12%) | 36/28/36 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Japan | Sweden | 1.78 | 0.98 | **1-0** | 1-0 (12%), 2-0 (10%), 1-1 (9%) | 56/21/23 |
| Tunisia | Netherlands | 0.65 | 1.85 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (11%) | 9/25/66 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Egypt | Iran | 0.94 | 1.07 | **0-0** | 0-0 (15%), 1-0 (14%), 0-1 (13%) | 33/30/37 |
| New Zealand | Belgium | 0.76 | 1.98 | **0-1** | 0-1 (13%), 1-1 (12%), 0-2 (11%) | 9/28/63 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Cape Verde | Saudi Arabia | 0.89 | 1.12 | **0-1** | 0-1 (16%), 0-0 (13%), 1-0 (13%) | 32/25/43 |
| Uruguay | Spain | 0.77 | 1.50 | **0-1** | 0-1 (15%), 0-0 (14%), 1-1 (12%) | 17/30/53 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Iraq | 2.01 | 0.48 | **1-0** | 1-0 (21%), 2-0 (16%), 2-1 (10%) | 78/17/6 |
| Norway | Senegal | 1.24 | 1.07 | **1-0** | 1-0 (14%), 0-0 (11%), 1-1 (10%) | 43/25/31 |
| Norway | France | 0.88 | 1.65 | **0-1** | 0-1 (13%), 1-1 (11%), 0-0 (11%) | 20/26/54 |
| Senegal | Iraq | 1.41 | 0.63 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 56/28/16 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Austria | 1.89 | 0.62 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (11%) | 66/24/10 |
| Jordan | Algeria | 0.87 | 1.69 | **0-1** | 0-1 (12%), 1-1 (12%), 0-0 (12%) | 17/29/54 |
| Algeria | Austria | 1.18 | 1.31 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (11%) | 31/27/42 |
| Jordan | Argentina | 0.51 | 2.25 | **0-1** | 0-1 (15%), 0-2 (14%), 0-0 (10%) | 4/22/73 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | Uzbekistan | 1.70 | 0.71 | **1-0** | 1-0 (16%), 2-0 (12%), 0-0 (11%) | 61/23/16 |
| Colombia | DR Congo | 1.77 | 0.52 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (11%) | 69/21/9 |
| Colombia | Portugal | 1.21 | 1.11 | **1-0** | 1-0 (13%), 0-0 (12%), 1-1 (11%) | 39/27/33 |
| DR Congo | Uzbekistan | 0.88 | 1.07 | **0-1** | 0-1 (16%), 0-0 (15%), 1-0 (14%) | 32/28/40 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Ghana | 2.01 | 0.48 | **1-0** | 1-0 (21%), 2-0 (16%), 3-0 (9%) | 77/17/6 |
| Panama | Croatia | 0.90 | 1.56 | **0-1** | 0-1 (13%), 0-0 (11%), 1-1 (11%) | 22/27/51 |
| Panama | England | 0.57 | 1.95 | **0-1** | 0-1 (16%), 0-2 (13%), 0-0 (12%) | 6/26/68 |
| Croatia | Ghana | 1.63 | 0.69 | **1-0** | 1-0 (17%), 0-0 (12%), 2-0 (12%) | 60/27/13 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: Colombia** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): B, D, E, G, I, J, K, L

**R32**  
- Ivory Coast 0-1 Paraguay → **Paraguay** (31% / 41% to win)
- France 1-0 Egypt → **France** (66% / 12% to win)
- South Korea 0-1 Canada → **Canada** (32% / 41% to win)
- Netherlands 1-1 Brazil → **Brazil** (30% / 43% to win)
- Morocco 1-0 Japan → **Morocco** (43% / 30% to win)
- Germany 1-0 Senegal → **Germany** (58% / 22% to win)
- Mexico 0-0 Ecuador → **Mexico** (38% / 31% to win)
- England 1-0 Uzbekistan → **England** (69% / 11% to win)
- Portugal 1-0 Croatia → **Portugal** (45% / 28% to win)
- Spain 1-0 Algeria → **Spain** (68% / 11% to win)
- United States 1-1 Switzerland → **Switzerland** (29% / 41% to win)
- Belgium 1-1 Norway → **Belgium** (41% / 32% to win)
- Argentina 1-0 Saudi Arabia → **Argentina** (74% / 4% to win)
- Australia 0-0 Iran → **Australia** (37% / 34% to win)
- Bosnia and Herzegovina 0-1 Austria → **Austria** (16% / 54% to win)
- Colombia 1-0 Panama → **Colombia** (70% / 10% to win)

**R16**  
- Paraguay 0-1 France → **France** (15% / 58% to win)
- Canada 0-1 Brazil → **Brazil** (15% / 56% to win)
- Morocco 1-0 Germany → **Morocco** (38% / 36% to win)
- Mexico 0-1 England → **England** (17% / 50% to win)
- Portugal 0-1 Spain → **Spain** (20% / 49% to win)
- Switzerland 1-1 Belgium → **Belgium** (32% / 38% to win)
- Argentina 1-0 Australia → **Argentina** (65% / 10% to win)
- Austria 0-1 Colombia → **Colombia** (20% / 55% to win)

**QF**  
- France 0-1 Brazil → **Brazil** (33% / 43% to win)
- Morocco 0-1 England → **England** (26% / 44% to win)
- Spain 1-0 Belgium → **Spain** (54% / 19% to win)
- Argentina 1-0 Colombia → **Argentina** (48% / 25% to win)

**SF**  
- Brazil 0-1 England → **England** (33% / 42% to win)
- Spain 0-0 Argentina → **Argentina** (32% / 35% to win)

**Final**  
- England 0-1 Argentina → **Argentina** (28% / 46% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): F, E, D, L, H, K, J, A

**R32**  
- Ivory Coast 2-2 Australia → **Australia** *(pens)*
- France 1-2 Netherlands → **Netherlands**
- South Korea 0-2 Canada → **Canada**
- Japan 2-0 Morocco → **Japan**
- Brazil 0-0 Sweden → **Brazil** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 4-3 Saudi Arabia → **Mexico**
- England 1-3 Colombia → **Colombia**
- Uzbekistan 0-3 Croatia → **Croatia**
- Uruguay 1-1 Austria → **Austria** *(pens)*
- Paraguay 0-1 Ecuador → **Ecuador**
- Belgium 2-0 Czechia → **Belgium**
- Argentina 2-0 Spain → **Argentina**
- United States 0-3 Egypt → **Egypt**
- Switzerland 1-2 Algeria → **Algeria**
- Portugal 3-0 Panama → **Portugal**

**R16**  
- Australia 2-4 Netherlands → **Netherlands**
- Canada 0-1 Japan → **Japan**
- Brazil 4-2 Germany → **Brazil**
- Mexico 0-0 Colombia → **Colombia** *(pens)*
- Croatia 2-2 Austria → **Croatia** *(pens)*
- Ecuador 1-0 Belgium → **Ecuador**
- Argentina 3-0 Egypt → **Argentina**
- Algeria 0-0 Portugal → **Portugal** *(pens)*

**QF**  
- Netherlands 2-4 Japan → **Japan**
- Brazil 1-1 Colombia → **Colombia** *(pens)*
- Croatia 0-1 Ecuador → **Ecuador**
- Argentina 0-2 Portugal → **Portugal**

**SF**  
- Japan 0-3 Colombia → **Colombia**
- Ecuador 0-1 Portugal → **Portugal**

**Final**  
- Colombia 1-0 Portugal → **Colombia**

**Sampled-scenario champion: Colombia** 🏆
