# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.2.0, rating_sigma=0, per-confederation calibration on). As-of 2026-06-07; generated 2026-06-11. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | South Africa | 1.94 | 0.64 | **1-0** | 1-0 (18%), 2-0 (16%), 2-1 (12%) | 75/15/10 |
| South Korea | Czechia | 1.49 | 1.17 | **1-1** | 1-1 (13%), 1-0 (9%), 2-1 (9%) | 43/28/29 |
| Czechia | South Africa | 1.44 | 0.87 | **1-0** | 1-0 (17%), 1-1 (12%), 2-1 (11%) | 55/26/20 |
| Mexico | South Korea | 1.74 | 0.96 | **1-1** | 1-1 (13%), 1-0 (12%), 2-1 (11%) | 56/27/16 |
| Mexico | Czechia | 1.98 | 0.88 | **1-1** | 1-1 (14%), 1-0 (11%), 2-0 (11%) | 61/29/10 |
| South Africa | South Korea | 0.78 | 1.48 | **0-1** | 0-1 (16%), 1-1 (14%), 0-0 (11%) | 17/29/54 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Bosnia and Herzegovina | 2.11 | 0.69 | **2-0** | 2-0 (14%), 1-0 (14%), 2-1 (10%) | 73/16/11 |
| Qatar | Switzerland | 0.79 | 2.13 | **0-2** | 0-2 (12%), 0-1 (12%), 1-2 (12%) | 8/21/70 |
| Switzerland | Bosnia and Herzegovina | 1.95 | 0.70 | **1-0** | 1-0 (15%), 2-0 (14%), 2-1 (11%) | 70/21/10 |
| Canada | Qatar | 2.40 | 0.71 | **2-0** | 2-0 (13%), 1-0 (12%), 2-1 (11%) | 78/17/5 |
| Canada | Switzerland | 1.31 | 1.33 | **1-1** | 1-1 (15%), 0-1 (9%), 1-2 (9%) | 31/32/37 |
| Bosnia and Herzegovina | Qatar | 1.38 | 1.02 | **1-1** | 1-1 (14%), 1-0 (14%), 2-1 (10%) | 47/30/23 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Brazil | Morocco | 1.32 | 0.94 | **1-0** | 1-0 (17%), 2-1 (11%), 1-1 (11%) | 51/24/25 |
| Haiti | Scotland | 1.23 | 1.61 | **1-1** | 1-1 (12%), 1-2 (12%), 0-1 (11%) | 24/27/49 |
| Scotland | Morocco | 0.76 | 1.46 | **0-1** | 0-1 (15%), 1-1 (12%), 0-2 (12%) | 21/27/52 |
| Brazil | Haiti | 2.40 | 0.87 | **2-1** | 2-1 (14%), 2-0 (12%), 1-0 (11%) | 78/17/5 |
| Scotland | Brazil | 0.90 | 1.93 | **1-1** | 1-1 (11%), 0-1 (11%), 0-2 (11%) | 14/24/62 |
| Morocco | Haiti | 1.92 | 0.68 | **1-0** | 1-0 (17%), 2-0 (14%), 2-1 (12%) | 72/19/9 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Paraguay | 1.33 | 1.25 | **1-1** | 1-1 (12%), 0-1 (11%), 1-2 (10%) | 37/25/38 |
| Australia | Türkiye | 1.24 | 1.29 | **1-1** | 1-1 (13%), 0-1 (12%), 1-2 (10%) | 33/26/40 |
| United States | Australia | 1.34 | 1.48 | **1-1** | 1-1 (12%), 1-2 (9%), 0-1 (9%) | 33/25/42 |
| Türkiye | Paraguay | 1.21 | 1.13 | **1-0** | 1-0 (13%), 0-1 (12%), 1-1 (10%) | 41/22/37 |
| United States | Türkiye | 1.76 | 1.57 | **1-2** | 1-2 (9%), 1-1 (8%), 2-1 (8%) | 42/19/38 |
| Paraguay | Australia | 1.02 | 0.98 | **1-0** | 1-0 (17%), 0-0 (12%), 1-1 (12%) | 40/27/32 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Curaçao | 2.44 | 0.79 | **2-1** | 2-1 (13%), 2-0 (13%), 1-0 (12%) | 81/15/5 |
| Ivory Coast | Ecuador | 0.60 | 1.13 | **0-1** | 0-1 (25%), 0-0 (16%), 1-1 (11%) | 17/29/54 |
| Germany | Ivory Coast | 1.70 | 0.91 | **1-0** | 1-0 (17%), 2-1 (14%), 2-0 (12%) | 65/16/19 |
| Ecuador | Curaçao | 1.73 | 0.46 | **1-0** | 1-0 (25%), 2-0 (17%), 2-1 (12%) | 76/20/3 |
| Curaçao | Ivory Coast | 0.79 | 1.64 | **0-1** | 0-1 (15%), 1-1 (12%), 0-2 (12%) | 16/26/59 |
| Ecuador | Germany | 1.16 | 0.99 | **1-0** | 1-0 (16%), 1-1 (12%), 0-0 (11%) | 43/27/31 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Japan | 1.50 | 1.14 | **1-1** | 1-1 (13%), 1-0 (13%), 2-1 (12%) | 49/28/23 |
| Sweden | Tunisia | 1.30 | 1.19 | **1-0** | 1-0 (14%), 2-1 (10%), 0-1 (10%) | 45/19/35 |
| Netherlands | Sweden | 2.08 | 1.07 | **1-1** | 1-1 (11%), 2-1 (10%), 2-0 (9%) | 60/24/16 |
| Tunisia | Japan | 0.73 | 1.50 | **0-1** | 0-1 (15%), 1-1 (14%), 0-0 (12%) | 15/30/54 |
| Japan | Sweden | 2.00 | 0.97 | **1-1** | 1-1 (11%), 2-0 (10%), 2-1 (9%) | 59/24/17 |
| Tunisia | Netherlands | 0.72 | 1.71 | **0-1** | 0-1 (18%), 0-2 (13%), 1-2 (12%) | 11/24/65 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.41 | 0.93 | **1-0** | 1-0 (15%), 2-0 (10%), 2-1 (10%) | 52/21/27 |
| Iran | New Zealand | 1.78 | 0.88 | **1-1** | 1-1 (14%), 1-0 (13%), 2-1 (11%) | 58/29/12 |
| Belgium | Iran | 1.61 | 1.13 | **1-0** | 1-0 (13%), 2-1 (12%), 2-0 (9%) | 54/19/26 |
| New Zealand | Egypt | 0.77 | 1.40 | **0-1** | 0-1 (17%), 1-1 (15%), 0-0 (13%) | 15/33/52 |
| Egypt | Iran | 0.96 | 1.22 | **0-1** | 0-1 (15%), 1-0 (12%), 1-1 (11%) | 31/25/44 |
| New Zealand | Belgium | 0.85 | 2.01 | **0-1** | 0-1 (12%), 1-2 (12%), 1-1 (12%) | 8/26/66 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.31 | 0.58 | **2-0** | 2-0 (16%), 1-0 (15%), 2-1 (12%) | 82/15/3 |
| Saudi Arabia | Uruguay | 0.48 | 1.42 | **0-1** | 0-1 (26%), 0-0 (15%), 0-2 (14%) | 7/29/65 |
| Spain | Saudi Arabia | 2.17 | 0.55 | **1-0** | 1-0 (18%), 2-0 (17%), 2-1 (12%) | 82/15/3 |
| Uruguay | Cape Verde | 1.59 | 0.51 | **1-0** | 1-0 (26%), 2-0 (16%), 2-1 (12%) | 72/18/9 |
| Cape Verde | Saudi Arabia | 0.98 | 1.09 | **0-1** | 0-1 (14%), 1-0 (13%), 1-1 (12%) | 33/28/39 |
| Uruguay | Spain | 0.83 | 1.39 | **0-1** | 0-1 (15%), 1-1 (13%), 0-0 (11%) | 22/28/50 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.63 | 0.93 | **1-0** | 1-0 (16%), 2-1 (13%), 1-1 (12%) | 59/24/17 |
| Iraq | Norway | 0.76 | 1.56 | **0-1** | 0-1 (17%), 1-1 (12%), 0-2 (12%) | 15/27/58 |
| France | Iraq | 1.81 | 0.55 | **1-0** | 1-0 (22%), 2-0 (16%), 2-1 (13%) | 76/19/5 |
| Norway | Senegal | 1.46 | 1.20 | **1-0** | 1-0 (12%), 1-1 (12%), 2-1 (11%) | 46/25/29 |
| Norway | France | 1.05 | 1.67 | **1-1** | 1-1 (15%), 0-1 (11%), 1-2 (11%) | 17/31/52 |
| Senegal | Iraq | 1.44 | 0.73 | **1-0** | 1-0 (17%), 2-0 (12%), 1-1 (12%) | 55/26/18 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.76 | 0.71 | **1-0** | 1-0 (18%), 2-0 (13%), 2-1 (13%) | 68/22/9 |
| Austria | Jordan | 1.58 | 1.09 | **1-0** | 1-0 (11%), 1-1 (11%), 2-1 (10%) | 50/23/27 |
| Argentina | Austria | 1.79 | 0.68 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (12%) | 71/16/13 |
| Jordan | Algeria | 1.09 | 1.69 | **1-1** | 1-1 (14%), 0-1 (9%), 1-2 (8%) | 23/30/47 |
| Algeria | Austria | 1.18 | 1.24 | **1-1** | 1-1 (14%), 0-1 (12%), 0-0 (10%) | 31/29/39 |
| Jordan | Argentina | 0.69 | 2.07 | **1-1** | 1-1 (14%), 0-2 (13%), 0-1 (12%) | 4/29/67 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.53 | 0.64 | **1-0** | 1-0 (20%), 2-0 (14%), 1-1 (11%) | 63/25/13 |
| Uzbekistan | Colombia | 0.73 | 1.50 | **0-1** | 0-1 (17%), 1-1 (14%), 0-0 (12%) | 13/30/56 |
| Portugal | Uzbekistan | 1.61 | 0.75 | **1-0** | 1-0 (17%), 2-0 (12%), 1-1 (11%) | 61/24/14 |
| Colombia | DR Congo | 1.54 | 0.58 | **1-0** | 1-0 (23%), 2-0 (14%), 2-1 (11%) | 66/25/9 |
| Colombia | Portugal | 1.43 | 1.25 | **1-1** | 1-1 (13%), 1-0 (10%), 2-1 (10%) | 42/27/31 |
| DR Congo | Uzbekistan | 0.80 | 0.91 | **0-1** | 0-1 (18%), 0-0 (17%), 1-0 (15%) | 31/30/39 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.39 | 0.92 | **1-0** | 1-0 (14%), 1-1 (12%), 0-0 (10%) | 49/27/25 |
| Ghana | Panama | 0.93 | 1.58 | **0-1** | 0-1 (14%), 1-1 (13%), 1-2 (12%) | 18/26/55 |
| England | Ghana | 1.90 | 0.52 | **1-0** | 1-0 (19%), 2-0 (16%), 2-1 (11%) | 74/23/3 |
| Panama | Croatia | 0.95 | 1.70 | **1-1** | 1-1 (13%), 0-1 (13%), 1-2 (11%) | 17/28/56 |
| Panama | England | 0.79 | 1.76 | **1-1** | 1-1 (14%), 0-1 (13%), 0-2 (12%) | 12/29/59 |
| Croatia | Ghana | 1.82 | 0.68 | **1-0** | 1-0 (19%), 2-0 (14%), 2-1 (13%) | 71/19/10 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Switzerland** (seed 7)

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
- Portugal 1-1 Croatia → **Portugal** (49% / 26% to win)
- Spain 1-0 Austria → **Spain** (66% / 11% to win)
- Türkiye 1-1 Algeria → **Türkiye** (40% / 37% to win)
- Belgium 2-1 Czechia → **Belgium** (61% / 16% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 14% to win)
- Paraguay 1-0 Iran → **Paraguay** (42% / 31% to win)
- Canada 1-0 Egypt → **Canada** (43% / 31% to win)
- Colombia 1-1 Panama → **Colombia** (61% / 13% to win)

**R16**  
- Ecuador 0-1 France → **France** (22% / 49% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (22% / 45% to win)
- Brazil 2-1 Germany → **Brazil** (52% / 28% to win)
- Mexico 0-1 England → **England** (22% / 48% to win)
- Portugal 1-1 Spain → **Spain** (18% / 54% to win)
- Türkiye 1-1 Belgium → **Belgium** (21% / 51% to win)
- Argentina 1-0 Paraguay → **Argentina** (58% / 9% to win)
- Canada 0-1 Colombia → **Colombia** (15% / 56% to win)

**QF**  
- France 1-1 Netherlands → **France** (45% / 29% to win)
- Brazil 1-1 England → **England** (25% / 46% to win)
- Spain 1-1 Belgium → **Spain** (58% / 17% to win)
- Argentina 1-1 Colombia → **Argentina** (49% / 21% to win)

**SF**  
- France 1-0 England → **France** (43% / 31% to win)
- Spain 1-0 Argentina → **Spain** (42% / 34% to win)

**Final**  
- France 1-1 Spain → **Spain** (21% / 52% to win)

**Chalk champion: Spain** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): G, E, K, F, J, A, D, C

**R32**  
- Ivory Coast 2-3 Türkiye → **Türkiye**
- France 1-2 Japan → **Japan**
- South Korea 1-2 Switzerland → **Switzerland**
- Netherlands 1-0 Brazil → **Netherlands**
- Morocco 2-1 Tunisia → **Morocco**
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 0-0 Scotland → **Mexico** *(pens)*
- England 4-0 DR Congo → **England**
- Uzbekistan 1-3 Panama → **Panama**
- Spain 2-0 Austria → **Spain**
- Paraguay 1-1 Algeria → **Algeria** *(pens)*
- Belgium 1-1 Czechia → **Belgium** *(pens)*
- Argentina 2-0 Uruguay → **Argentina**
- United States 1-0 Iran → **United States**
- Canada 1-1 Egypt → **Egypt** *(pens)*
- Portugal 3-0 Ecuador → **Portugal**

**R16**  
- Türkiye 0-1 Japan → **Japan**
- Switzerland 3-2 Netherlands → **Switzerland**
- Morocco 0-0 Germany → **Germany** *(pens)*
- Mexico 2-0 England → **Mexico**
- Panama 0-1 Spain → **Spain**
- Algeria 1-1 Belgium → **Belgium** *(pens)*
- Argentina 0-0 United States → **Argentina** *(pens)*
- Egypt 2-0 Portugal → **Egypt**

**QF**  
- Japan 1-2 Switzerland → **Switzerland**
- Germany 2-1 Mexico → **Germany**
- Spain 1-0 Belgium → **Spain**
- Argentina 1-0 Egypt → **Argentina**

**SF**  
- Switzerland 1-1 Germany → **Switzerland** *(pens)*
- Spain 1-0 Argentina → **Spain**

**Final**  
- Switzerland 3-1 Spain → **Switzerland**

**Sampled-scenario champion: Switzerland** 🏆
