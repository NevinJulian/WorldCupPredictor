# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-07; generated 2026-06-13. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | South Africa | 2.03 | 0.61 | **1-0** | 1-0 (17%), 2-0 (15%), 2-1 (9%) | 73/16/11 |
| South Korea | Czechia | 1.35 | 1.04 | **0-0** | 0-0 (12%), 1-1 (12%), 1-0 (12%) | 42/28/29 |
| Czechia | South Africa | 1.34 | 0.77 | **1-0** | 1-0 (18%), 0-0 (13%), 2-0 (11%) | 52/27/21 |
| Mexico | South Korea | 1.74 | 0.92 | **1-0** | 1-0 (13%), 1-1 (12%), 0-0 (10%) | 55/27/18 |
| Mexico | Czechia | 2.00 | 0.84 | **1-1** | 1-1 (12%), 1-0 (11%), 2-0 (10%) | 60/28/12 |
| South Africa | South Korea | 0.68 | 1.37 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (11%) | 17/30/53 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Bosnia and Herzegovina | 2.16 | 0.72 | **1-0** | 1-0 (14%), 2-0 (13%), 2-1 (9%) | 71/17/12 |
| Qatar | Switzerland | 0.73 | 2.00 | **0-1** | 0-1 (15%), 0-2 (12%), 1-2 (10%) | 10/22/68 |
| Switzerland | Bosnia and Herzegovina | 1.87 | 0.66 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (10%) | 67/22/11 |
| Canada | Qatar | 2.39 | 0.74 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (10%) | 75/18/7 |
| Canada | Switzerland | 1.31 | 1.31 | **1-1** | 1-1 (13%), 0-0 (11%), 0-1 (10%) | 33/31/36 |
| Bosnia and Herzegovina | Qatar | 1.32 | 1.02 | **1-0** | 1-0 (14%), 0-0 (13%), 1-1 (12%) | 45/30/25 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Brazil | Morocco | 1.38 | 0.76 | **1-0** | 1-0 (17%), 0-0 (13%), 2-0 (11%) | 52/25/23 |
| Haiti | Scotland | 1.07 | 1.53 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (10%) | 25/27/49 |
| Scotland | Morocco | 0.68 | 1.36 | **0-1** | 0-1 (17%), 0-0 (15%), 0-2 (11%) | 20/28/52 |
| Brazil | Haiti | 2.79 | 0.62 | **2-0** | 2-0 (12%), 1-0 (11%), 3-0 (10%) | 80/16/4 |
| Scotland | Brazil | 0.66 | 2.06 | **0-1** | 0-1 (13%), 0-2 (12%), 0-0 (10%) | 13/23/65 |
| Morocco | Haiti | 1.92 | 0.61 | **1-0** | 1-0 (18%), 2-0 (14%), 2-1 (9%) | 70/20/10 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Paraguay | 1.33 | 1.11 | **0-1** | 0-1 (12%), 0-0 (10%), 1-1 (10%) | 39/25/36 |
| Australia | Türkiye | 1.27 | 1.21 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (11%) | 35/26/38 |
| United States | Australia | 1.34 | 1.37 | **1-1** | 1-1 (11%), 0-1 (10%), 0-0 (9%) | 35/26/39 |
| Türkiye | Paraguay | 1.15 | 1.10 | **1-0** | 1-0 (13%), 0-1 (13%), 0-0 (11%) | 40/24/37 |
| United States | Türkiye | 1.71 | 1.33 | **0-1** | 0-1 (9%), 1-1 (9%), 1-2 (8%) | 45/20/36 |
| Paraguay | Australia | 1.01 | 1.03 | **1-0** | 1-0 (16%), 0-0 (14%), 0-1 (12%) | 38/28/34 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Curaçao | 2.82 | 0.67 | **2-0** | 2-0 (12%), 1-0 (11%), 3-0 (10%) | 81/14/4 |
| Ivory Coast | Ecuador | 0.72 | 1.27 | **0-1** | 0-1 (19%), 0-0 (15%), 1-1 (11%) | 19/30/51 |
| Germany | Ivory Coast | 1.85 | 0.92 | **1-0** | 1-0 (15%), 2-0 (11%), 2-1 (10%) | 63/17/19 |
| Ecuador | Curaçao | 2.04 | 0.50 | **1-0** | 1-0 (19%), 2-0 (15%), 0-0 (10%) | 75/20/4 |
| Curaçao | Ivory Coast | 0.73 | 1.78 | **0-1** | 0-1 (14%), 0-2 (12%), 0-0 (11%) | 15/25/60 |
| Ecuador | Germany | 1.23 | 1.18 | **1-0** | 1-0 (13%), 1-1 (11%), 0-0 (11%) | 40/27/33 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Japan | 1.51 | 1.09 | **1-0** | 1-0 (12%), 1-1 (12%), 0-0 (10%) | 48/28/24 |
| Sweden | Tunisia | 1.20 | 1.03 | **1-0** | 1-0 (15%), 0-1 (12%), 0-0 (10%) | 44/22/34 |
| Netherlands | Sweden | 1.84 | 0.90 | **1-0** | 1-0 (13%), 1-1 (10%), 2-0 (10%) | 59/24/17 |
| Tunisia | Japan | 0.73 | 1.47 | **0-1** | 0-1 (16%), 0-0 (14%), 1-1 (12%) | 17/30/53 |
| Japan | Sweden | 1.73 | 0.91 | **1-0** | 1-0 (13%), 1-1 (10%), 2-0 (10%) | 56/24/19 |
| Tunisia | Netherlands | 0.67 | 1.70 | **0-1** | 0-1 (18%), 0-2 (13%), 0-0 (11%) | 12/25/63 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.46 | 0.90 | **1-0** | 1-0 (15%), 2-0 (10%), 0-0 (10%) | 52/23/26 |
| Iran | New Zealand | 1.65 | 0.72 | **1-0** | 1-0 (16%), 0-0 (13%), 1-1 (12%) | 58/29/13 |
| Belgium | Iran | 1.49 | 1.02 | **1-0** | 1-0 (15%), 2-0 (10%), 2-1 (9%) | 52/21/27 |
| New Zealand | Egypt | 0.74 | 1.37 | **0-1** | 0-1 (17%), 0-0 (16%), 1-1 (13%) | 16/33/51 |
| Egypt | Iran | 0.89 | 1.18 | **0-1** | 0-1 (15%), 0-0 (13%), 1-0 (13%) | 30/26/44 |
| New Zealand | Belgium | 0.74 | 2.01 | **0-1** | 0-1 (14%), 0-2 (12%), 1-1 (11%) | 8/26/66 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.41 | 0.46 | **1-0** | 1-0 (16%), 2-0 (16%), 3-0 (11%) | 81/15/3 |
| Saudi Arabia | Uruguay | 0.51 | 1.61 | **0-1** | 0-1 (20%), 0-0 (15%), 0-2 (14%) | 8/28/64 |
| Spain | Saudi Arabia | 2.26 | 0.49 | **1-0** | 1-0 (18%), 2-0 (16%), 3-0 (10%) | 80/16/4 |
| Uruguay | Cape Verde | 1.81 | 0.50 | **1-0** | 1-0 (21%), 2-0 (16%), 0-0 (10%) | 72/19/9 |
| Cape Verde | Saudi Arabia | 0.91 | 1.07 | **0-0** | 0-0 (15%), 0-1 (14%), 1-0 (13%) | 32/29/39 |
| Uruguay | Spain | 0.85 | 1.41 | **0-1** | 0-1 (15%), 0-0 (13%), 1-1 (11%) | 22/28/49 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.53 | 0.74 | **1-0** | 1-0 (18%), 0-0 (12%), 2-0 (12%) | 58/25/17 |
| Iraq | Norway | 0.72 | 1.46 | **0-1** | 0-1 (18%), 0-0 (13%), 0-2 (11%) | 16/28/56 |
| France | Iraq | 1.89 | 0.49 | **1-0** | 1-0 (21%), 2-0 (16%), 0-0 (10%) | 74/20/6 |
| Norway | Senegal | 1.23 | 1.05 | **1-0** | 1-0 (15%), 0-0 (12%), 1-1 (11%) | 44/26/30 |
| Norway | France | 0.83 | 1.62 | **0-1** | 0-1 (13%), 1-1 (13%), 0-0 (13%) | 17/30/53 |
| Senegal | Iraq | 1.35 | 0.67 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 54/27/19 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.94 | 0.66 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (10%) | 68/22/10 |
| Austria | Jordan | 1.47 | 0.96 | **1-0** | 1-0 (14%), 0-0 (10%), 1-1 (10%) | 50/24/26 |
| Argentina | Austria | 1.97 | 0.63 | **1-0** | 1-0 (17%), 2-0 (14%), 2-1 (9%) | 70/17/13 |
| Jordan | Algeria | 0.95 | 1.56 | **1-1** | 1-1 (12%), 0-0 (12%), 0-1 (11%) | 22/30/48 |
| Algeria | Austria | 1.20 | 1.24 | **1-1** | 1-1 (12%), 0-0 (12%), 0-1 (12%) | 33/29/38 |
| Jordan | Argentina | 0.52 | 2.13 | **0-1** | 0-1 (14%), 0-2 (13%), 0-0 (12%) | 4/27/69 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.76 | 0.60 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (12%) | 64/24/12 |
| Uzbekistan | Colombia | 0.63 | 1.51 | **0-1** | 0-1 (17%), 0-0 (15%), 0-2 (12%) | 14/30/57 |
| Portugal | Uzbekistan | 1.68 | 0.68 | **1-0** | 1-0 (17%), 2-0 (12%), 0-0 (12%) | 61/25/14 |
| Colombia | DR Congo | 1.71 | 0.52 | **1-0** | 1-0 (20%), 2-0 (14%), 0-0 (13%) | 66/24/9 |
| Colombia | Portugal | 1.22 | 1.07 | **1-0** | 1-0 (13%), 0-0 (12%), 1-1 (11%) | 41/27/32 |
| DR Congo | Uzbekistan | 0.85 | 1.05 | **0-0** | 0-0 (17%), 0-1 (15%), 1-0 (13%) | 30/30/39 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.37 | 0.85 | **1-0** | 1-0 (15%), 0-0 (13%), 1-1 (11%) | 49/27/24 |
| Ghana | Panama | 0.89 | 1.38 | **0-1** | 0-1 (16%), 0-0 (12%), 1-1 (11%) | 22/27/51 |
| England | Ghana | 1.92 | 0.47 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (12%) | 73/23/4 |
| Panama | Croatia | 0.81 | 1.64 | **0-1** | 0-1 (14%), 0-0 (12%), 1-1 (11%) | 17/28/56 |
| Panama | England | 0.64 | 1.78 | **0-1** | 0-1 (15%), 0-0 (13%), 0-2 (12%) | 12/28/61 |
| Croatia | Ghana | 1.76 | 0.64 | **1-0** | 1-0 (20%), 2-0 (14%), 2-1 (10%) | 68/20/12 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Spain** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, C, D, E, G, I, J, L

**R32**  
- Germany 1-0 Scotland → **Germany** (58% / 20% to win)
- France 1-0 Paraguay → **France** (59% / 16% to win)
- South Korea 0-1 Switzerland → **Switzerland** (20% / 51% to win)
- Netherlands 1-0 Morocco → **Netherlands** (47% / 29% to win)
- Brazil 1-0 Japan → **Brazil** (55% / 20% to win)
- Ecuador 1-0 Norway → **Ecuador** (43% / 28% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (49% / 24% to win)
- England 1-0 Senegal → **England** (53% / 19% to win)
- Portugal 1-0 Croatia → **Portugal** (49% / 26% to win)
- Spain 1-0 Austria → **Spain** (66% / 11% to win)
- United States 1-1 Algeria → **Algeria** (33% / 41% to win)
- Belgium 1-0 Czechia → **Belgium** (60% / 17% to win)
- Argentina 1-0 Uruguay → **Argentina** (53% / 16% to win)
- Türkiye 1-0 Iran → **Iran** (38% / 39% to win)
- Canada 1-0 Egypt → **Canada** (41% / 31% to win)
- Colombia 1-0 Panama → **Colombia** (62% / 13% to win)

**R16**  
- Germany 1-1 France → **France** (31% / 42% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (22% / 45% to win)
- Brazil 1-0 Ecuador → **Brazil** (49% / 25% to win)
- Mexico 0-1 England → **England** (22% / 48% to win)
- Portugal 0-1 Spain → **Spain** (20% / 52% to win)
- Algeria 1-1 Belgium → **Belgium** (22% / 50% to win)
- Argentina 1-0 Iran → **Argentina** (65% / 10% to win)
- Canada 0-1 Colombia → **Colombia** (16% / 56% to win)

**QF**  
- France 1-0 Netherlands → **France** (44% / 29% to win)
- Brazil 0-1 England → **England** (29% / 42% to win)
- Spain 1-0 Belgium → **Spain** (56% / 18% to win)
- Argentina 1-0 Colombia → **Argentina** (48% / 22% to win)

**SF**  
- France 1-0 England → **France** (42% / 31% to win)
- Spain 1-0 Argentina → **Spain** (40% / 34% to win)

**Final**  
- France 0-1 Spain → **Spain** (22% / 50% to win)

**Chalk champion: Spain** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): G, E, H, I, A, K, C, J

**R32**  
- Germany 5-0 Haiti → **Germany**
- France 2-0 Saudi Arabia → **France**
- South Korea 1-1 Canada → **South Korea** *(pens)*
- Netherlands 2-1 Brazil → **Netherlands**
- Morocco 0-0 Sweden → **Morocco** *(pens)*
- Ecuador 0-0 Iraq → **Ecuador** *(pens)*
- Mexico 6-0 Curaçao → **Mexico**
- England 2-1 DR Congo → **England**
- Uzbekistan 1-0 Panama → **Uzbekistan**
- Uruguay 1-1 Algeria → **Algeria** *(pens)*
- Paraguay 0-3 Austria → **Austria**
- Egypt 1-2 Czechia → **Czechia**
- Argentina 1-3 Spain → **Spain**
- Türkiye 0-4 Belgium → **Belgium**
- Switzerland 1-1 Iran → **Iran** *(pens)*
- Portugal 3-2 Senegal → **Portugal**

**R16**  
- Germany 0-1 France → **France**
- South Korea 3-0 Netherlands → **South Korea**
- Morocco 0-0 Ecuador → **Ecuador** *(pens)*
- Mexico 2-0 England → **Mexico**
- Uzbekistan 0-0 Algeria → **Algeria** *(pens)*
- Austria 2-3 Czechia → **Czechia**
- Spain 0-0 Belgium → **Spain** *(pens)*
- Iran 2-0 Portugal → **Iran**

**QF**  
- France 1-3 South Korea → **South Korea**
- Ecuador 2-0 Mexico → **Ecuador**
- Algeria 0-2 Czechia → **Czechia**
- Spain 1-0 Iran → **Spain**

**SF**  
- South Korea 0-2 Ecuador → **Ecuador**
- Czechia 0-1 Spain → **Spain**

**Final**  
- Ecuador 0-2 Spain → **Spain**

**Sampled-scenario champion: Spain** 🏆
