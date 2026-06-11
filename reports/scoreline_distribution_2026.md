# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.3.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-07; generated 2026-06-11. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | South Africa | 2.01 | 0.62 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 75/15/10 |
| South Korea | Czechia | 1.50 | 1.15 | **1-1** | 1-1 (12%), 0-0 (10%), 1-0 (10%) | 43/28/29 |
| Czechia | South Africa | 1.46 | 0.86 | **1-0** | 1-0 (17%), 0-0 (11%), 1-1 (11%) | 55/26/20 |
| Mexico | South Korea | 1.77 | 0.93 | **1-0** | 1-0 (13%), 1-1 (12%), 0-0 (10%) | 56/27/16 |
| Mexico | Czechia | 2.02 | 0.83 | **1-1** | 1-1 (12%), 1-0 (11%), 2-0 (10%) | 61/29/10 |
| South Africa | South Korea | 0.76 | 1.50 | **0-1** | 0-1 (16%), 0-0 (13%), 1-1 (12%) | 17/29/54 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Bosnia and Herzegovina | 2.18 | 0.66 | **1-0** | 1-0 (15%), 2-0 (14%), 3-0 (9%) | 73/16/11 |
| Qatar | Switzerland | 0.76 | 2.19 | **0-1** | 0-1 (13%), 0-2 (12%), 1-2 (10%) | 8/21/70 |
| Switzerland | Bosnia and Herzegovina | 2.01 | 0.67 | **1-0** | 1-0 (16%), 2-0 (13%), 2-1 (10%) | 70/21/10 |
| Canada | Qatar | 2.48 | 0.67 | **1-0** | 1-0 (13%), 2-0 (13%), 2-1 (9%) | 78/17/5 |
| Canada | Switzerland | 1.30 | 1.31 | **1-1** | 1-1 (14%), 0-0 (11%), 0-1 (10%) | 31/32/37 |
| Bosnia and Herzegovina | Qatar | 1.39 | 1.00 | **1-0** | 1-0 (14%), 1-1 (13%), 0-0 (12%) | 47/30/23 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Brazil | Morocco | 1.34 | 0.94 | **1-0** | 1-0 (18%), 0-0 (11%), 1-1 (10%) | 51/24/25 |
| Haiti | Scotland | 1.21 | 1.61 | **0-1** | 0-1 (11%), 1-1 (11%), 1-2 (10%) | 24/27/49 |
| Scotland | Morocco | 0.74 | 1.48 | **0-1** | 0-1 (15%), 0-0 (13%), 0-2 (11%) | 21/27/52 |
| Brazil | Haiti | 2.48 | 0.83 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (12%) | 78/17/5 |
| Scotland | Brazil | 0.87 | 1.98 | **0-1** | 0-1 (12%), 0-2 (11%), 1-1 (10%) | 14/24/62 |
| Morocco | Haiti | 1.98 | 0.65 | **1-0** | 1-0 (18%), 2-0 (14%), 2-1 (10%) | 72/19/9 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Paraguay | 1.34 | 1.24 | **0-1** | 0-1 (12%), 1-1 (10%), 0-0 (9%) | 37/25/38 |
| Australia | Türkiye | 1.24 | 1.28 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (10%) | 33/26/40 |
| United States | Australia | 1.33 | 1.48 | **1-1** | 1-1 (11%), 0-1 (10%), 0-0 (8%) | 33/25/42 |
| Türkiye | Paraguay | 1.22 | 1.13 | **1-0** | 1-0 (13%), 0-1 (12%), 0-0 (10%) | 41/22/37 |
| United States | Türkiye | 1.77 | 1.56 | **1-1** | 1-1 (8%), 1-2 (8%), 0-1 (7%) | 42/19/38 |
| Paraguay | Australia | 1.02 | 0.98 | **1-0** | 1-0 (17%), 0-0 (14%), 0-1 (11%) | 40/27/32 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Curaçao | 2.53 | 0.75 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (11%) | 81/15/5 |
| Ivory Coast | Ecuador | 0.60 | 1.14 | **0-1** | 0-1 (25%), 0-0 (18%), 0-2 (11%) | 17/29/54 |
| Germany | Ivory Coast | 1.75 | 0.90 | **1-0** | 1-0 (18%), 2-1 (12%), 2-0 (12%) | 65/16/19 |
| Ecuador | Curaçao | 1.79 | 0.45 | **1-0** | 1-0 (25%), 2-0 (16%), 2-1 (11%) | 76/20/3 |
| Curaçao | Ivory Coast | 0.76 | 1.68 | **0-1** | 0-1 (15%), 0-2 (11%), 0-0 (11%) | 16/26/59 |
| Ecuador | Germany | 1.16 | 0.99 | **1-0** | 1-0 (16%), 0-0 (13%), 1-1 (11%) | 43/27/31 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Japan | 1.51 | 1.12 | **1-0** | 1-0 (13%), 1-1 (12%), 0-0 (10%) | 49/28/23 |
| Sweden | Tunisia | 1.31 | 1.20 | **1-0** | 1-0 (14%), 0-1 (10%), 2-1 (9%) | 45/19/35 |
| Netherlands | Sweden | 2.12 | 1.03 | **1-1** | 1-1 (10%), 1-0 (10%), 2-0 (9%) | 60/24/16 |
| Tunisia | Japan | 0.70 | 1.53 | **0-1** | 0-1 (16%), 0-0 (14%), 1-1 (12%) | 15/30/54 |
| Japan | Sweden | 2.04 | 0.93 | **1-1** | 1-1 (10%), 1-0 (10%), 2-0 (10%) | 59/24/17 |
| Tunisia | Netherlands | 0.69 | 1.75 | **0-1** | 0-1 (18%), 0-2 (13%), 0-0 (11%) | 11/24/65 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.44 | 0.92 | **1-0** | 1-0 (16%), 2-0 (10%), 0-0 (10%) | 52/21/27 |
| Iran | New Zealand | 1.81 | 0.84 | **1-0** | 1-0 (13%), 1-1 (13%), 0-0 (11%) | 58/29/12 |
| Belgium | Iran | 1.63 | 1.12 | **1-0** | 1-0 (14%), 2-1 (10%), 2-0 (9%) | 54/19/26 |
| New Zealand | Egypt | 0.75 | 1.41 | **0-1** | 0-1 (17%), 0-0 (15%), 1-1 (13%) | 15/33/52 |
| Egypt | Iran | 0.95 | 1.24 | **0-1** | 0-1 (15%), 1-0 (12%), 0-0 (12%) | 31/25/44 |
| New Zealand | Belgium | 0.81 | 2.06 | **0-1** | 0-1 (13%), 1-1 (11%), 0-2 (11%) | 8/26/66 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.40 | 0.55 | **1-0** | 1-0 (16%), 2-0 (15%), 3-0 (10%) | 82/15/3 |
| Saudi Arabia | Uruguay | 0.46 | 1.45 | **0-1** | 0-1 (25%), 0-0 (16%), 0-2 (14%) | 7/29/65 |
| Spain | Saudi Arabia | 2.25 | 0.52 | **1-0** | 1-0 (19%), 2-0 (16%), 2-1 (11%) | 82/15/3 |
| Uruguay | Cape Verde | 1.64 | 0.50 | **1-0** | 1-0 (26%), 2-0 (16%), 2-1 (10%) | 72/18/9 |
| Cape Verde | Saudi Arabia | 0.98 | 1.09 | **0-1** | 0-1 (14%), 0-0 (14%), 1-0 (13%) | 33/28/39 |
| Uruguay | Spain | 0.81 | 1.41 | **0-1** | 0-1 (15%), 0-0 (13%), 1-1 (11%) | 22/28/50 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.66 | 0.91 | **1-0** | 1-0 (16%), 2-1 (11%), 2-0 (10%) | 59/24/17 |
| Iraq | Norway | 0.74 | 1.59 | **0-1** | 0-1 (17%), 0-0 (12%), 0-2 (12%) | 15/27/58 |
| France | Iraq | 1.87 | 0.53 | **1-0** | 1-0 (22%), 2-0 (15%), 2-1 (11%) | 76/19/5 |
| Norway | Senegal | 1.47 | 1.19 | **1-0** | 1-0 (12%), 1-1 (11%), 2-1 (9%) | 46/25/29 |
| Norway | France | 1.01 | 1.68 | **1-1** | 1-1 (13%), 0-1 (12%), 0-0 (11%) | 17/31/52 |
| Senegal | Iraq | 1.47 | 0.72 | **1-0** | 1-0 (17%), 0-0 (13%), 2-0 (12%) | 55/26/18 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.81 | 0.68 | **1-0** | 1-0 (19%), 2-0 (13%), 2-1 (11%) | 68/22/9 |
| Austria | Jordan | 1.60 | 1.07 | **1-0** | 1-0 (12%), 1-1 (10%), 2-0 (9%) | 50/23/27 |
| Argentina | Austria | 1.85 | 0.67 | **1-0** | 1-0 (19%), 2-0 (14%), 2-1 (10%) | 71/16/13 |
| Jordan | Algeria | 1.06 | 1.71 | **1-1** | 1-1 (13%), 0-0 (10%), 0-1 (9%) | 23/30/47 |
| Algeria | Austria | 1.17 | 1.23 | **0-1** | 0-1 (12%), 1-1 (12%), 0-0 (12%) | 31/29/39 |
| Jordan | Argentina | 0.64 | 2.12 | **0-1** | 0-1 (13%), 1-1 (12%), 0-2 (12%) | 4/29/67 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.56 | 0.62 | **1-0** | 1-0 (20%), 2-0 (13%), 0-0 (12%) | 63/25/13 |
| Uzbekistan | Colombia | 0.71 | 1.53 | **0-1** | 0-1 (17%), 0-0 (14%), 1-1 (12%) | 13/30/56 |
| Portugal | Uzbekistan | 1.65 | 0.73 | **1-0** | 1-0 (17%), 2-0 (12%), 0-0 (11%) | 61/24/14 |
| Colombia | DR Congo | 1.58 | 0.56 | **1-0** | 1-0 (23%), 2-0 (14%), 0-0 (13%) | 66/25/9 |
| Colombia | Portugal | 1.43 | 1.24 | **1-1** | 1-1 (11%), 1-0 (11%), 0-0 (9%) | 42/27/31 |
| DR Congo | Uzbekistan | 0.80 | 0.92 | **0-0** | 0-0 (18%), 0-1 (18%), 1-0 (15%) | 31/30/39 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.41 | 0.91 | **1-0** | 1-0 (14%), 0-0 (12%), 1-1 (11%) | 49/27/25 |
| Ghana | Panama | 0.91 | 1.60 | **0-1** | 0-1 (15%), 1-1 (11%), 0-0 (10%) | 18/26/55 |
| England | Ghana | 1.96 | 0.49 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (11%) | 74/23/3 |
| Panama | Croatia | 0.92 | 1.72 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (10%) | 17/28/56 |
| Panama | England | 0.75 | 1.79 | **0-1** | 0-1 (14%), 1-1 (12%), 0-0 (12%) | 12/29/59 |
| Croatia | Ghana | 1.87 | 0.66 | **1-0** | 1-0 (19%), 2-0 (14%), 2-1 (11%) | 71/19/10 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Argentina** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, C, D, E, G, I, J, L

**R32**  
- Ecuador 1-0 Scotland → **Ecuador** (56% / 16% to win)
- France 1-0 United States → **France** (74% / 9% to win)
- South Korea 0-1 Switzerland → **Switzerland** (18% / 54% to win)
- Netherlands 1-0 Morocco → **Netherlands** (48% / 30% to win)
- Brazil 1-0 Japan → **Brazil** (53% / 21% to win)
- Germany 1-1 Norway → **Germany** (46% / 30% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (51% / 22% to win)
- England 1-0 Senegal → **England** (54% / 20% to win)
- Portugal 1-0 Croatia → **Portugal** (49% / 26% to win)
- Spain 1-0 Austria → **Spain** (66% / 11% to win)
- Türkiye 1-0 Algeria → **Türkiye** (40% / 37% to win)
- Belgium 1-0 Czechia → **Belgium** (61% / 16% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 14% to win)
- Paraguay 1-0 Iran → **Paraguay** (42% / 31% to win)
- Canada 1-0 Egypt → **Canada** (43% / 31% to win)
- Colombia 1-0 Panama → **Colombia** (61% / 13% to win)

**R16**  
- Ecuador 0-1 France → **France** (22% / 49% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (22% / 45% to win)
- Brazil 1-0 Germany → **Brazil** (52% / 28% to win)
- Mexico 0-1 England → **England** (22% / 48% to win)
- Portugal 1-1 Spain → **Spain** (18% / 54% to win)
- Türkiye 1-1 Belgium → **Belgium** (21% / 51% to win)
- Argentina 0-0 Paraguay → **Argentina** (58% / 9% to win)
- Canada 0-1 Colombia → **Colombia** (15% / 56% to win)

**QF**  
- France 1-1 Netherlands → **France** (45% / 29% to win)
- Brazil 0-1 England → **England** (25% / 46% to win)
- Spain 1-0 Belgium → **Spain** (58% / 17% to win)
- Argentina 1-0 Colombia → **Argentina** (49% / 21% to win)

**SF**  
- France 1-0 England → **France** (43% / 31% to win)
- Spain 1-0 Argentina → **Spain** (42% / 34% to win)

**Final**  
- France 0-1 Spain → **Spain** (21% / 52% to win)

**Chalk champion: Spain** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): B, K, G, F, H, E, A, D

**R32**  
- Germany 4-0 Türkiye → **Germany**
- France 2-1 Sweden → **France**
- South Korea 2-1 Qatar → **South Korea**
- Netherlands 1-0 Brazil → **Netherlands**
- Morocco 2-0 Japan → **Morocco**
- Curaçao 0-0 Norway → **Norway** *(pens)*
- Mexico 0-0 Cape Verde → **Mexico** *(pens)*
- England 4-1 Uzbekistan → **England**
- DR Congo 1-2 Panama → **Panama**
- Spain 2-0 Algeria → **Spain**
- Paraguay 1-0 Canada → **Paraguay**
- Egypt 3-0 Czechia → **Egypt**
- Argentina 1-0 Uruguay → **Argentina**
- United States 1-2 Belgium → **Belgium**
- Switzerland 2-1 Iran → **Switzerland**
- Portugal 0-4 Ecuador → **Ecuador**

**R16**  
- Germany 1-2 France → **France**
- South Korea 2-0 Netherlands → **South Korea**
- Morocco 3-1 Norway → **Morocco**
- Mexico 0-1 England → **England**
- Panama 2-4 Spain → **Spain**
- Paraguay 0-0 Egypt → **Egypt** *(pens)*
- Argentina 3-1 Belgium → **Argentina**
- Switzerland 0-0 Ecuador → **Ecuador** *(pens)*

**QF**  
- France 3-1 South Korea → **France**
- Morocco 0-0 England → **England** *(pens)*
- Spain 3-0 Egypt → **Spain**
- Argentina 1-1 Ecuador → **Argentina** *(pens)*

**SF**  
- France 0-2 England → **England**
- Spain 0-2 Argentina → **Argentina**

**Final**  
- England 0-2 Argentina → **Argentina**

**Sampled-scenario champion: Argentina** 🏆
