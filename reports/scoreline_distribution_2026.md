# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-13; generated 2026-06-14. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Czechia | South Africa | 1.30 | 0.79 | **1-0** | 1-0 (17%), 0-0 (14%), 1-1 (11%) | 50/28/22 |
| Mexico | South Korea | 1.67 | 0.98 | **1-0** | 1-0 (12%), 1-1 (12%), 0-0 (10%) | 52/27/21 |
| Mexico | Czechia | 1.96 | 0.88 | **1-1** | 1-1 (12%), 1-0 (11%), 2-0 (10%) | 58/27/15 |
| South Africa | South Korea | 0.68 | 1.37 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (11%) | 18/29/53 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Switzerland | Bosnia and Herzegovina | 1.83 | 0.66 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (11%) | 65/24/11 |
| Canada | Qatar | 2.35 | 0.77 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (10%) | 75/15/10 |
| Canada | Switzerland | 1.34 | 1.29 | **1-1** | 1-1 (13%), 0-0 (11%), 0-1 (9%) | 35/30/35 |
| Bosnia and Herzegovina | Qatar | 1.36 | 1.04 | **1-0** | 1-0 (15%), 0-0 (10%), 1-1 (10%) | 48/24/28 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Morocco | 0.67 | 1.32 | **0-1** | 0-1 (17%), 0-0 (17%), 1-1 (11%) | 20/31/50 |
| Brazil | Haiti | 2.79 | 0.61 | **2-0** | 2-0 (13%), 1-0 (11%), 3-0 (10%) | 81/14/5 |
| Scotland | Brazil | 0.66 | 1.96 | **0-0** | 0-0 (12%), 0-1 (12%), 0-2 (12%) | 12/27/61 |
| Morocco | Haiti | 1.97 | 0.56 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 73/20/7 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Australia | 1.34 | 1.35 | **1-1** | 1-1 (12%), 0-1 (10%), 0-0 (10%) | 34/28/38 |
| Türkiye | Paraguay | 1.21 | 1.02 | **1-0** | 1-0 (14%), 0-0 (13%), 1-1 (11%) | 41/28/31 |
| United States | Türkiye | 1.70 | 1.28 | **1-1** | 1-1 (12%), 0-0 (8%), 0-1 (7%) | 42/27/31 |
| Paraguay | Australia | 0.86 | 1.21 | **0-1** | 0-1 (15%), 0-0 (14%), 1-0 (12%) | 28/29/43 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Curaçao | 2.76 | 0.71 | **2-0** | 2-0 (12%), 1-0 (10%), 3-0 (9%) | 79/14/7 |
| Ivory Coast | Ecuador | 0.70 | 1.29 | **0-1** | 0-1 (20%), 0-0 (16%), 1-1 (11%) | 18/30/53 |
| Germany | Ivory Coast | 1.79 | 0.96 | **1-0** | 1-0 (14%), 2-0 (11%), 2-1 (10%) | 60/18/22 |
| Ecuador | Curaçao | 2.03 | 0.52 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (9%) | 75/19/6 |
| Curaçao | Ivory Coast | 0.78 | 1.71 | **0-1** | 0-1 (13%), 0-0 (12%), 0-2 (11%) | 18/26/56 |
| Ecuador | Germany | 1.26 | 1.14 | **1-0** | 1-0 (13%), 1-1 (11%), 0-0 (11%) | 42/27/31 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Japan | 1.38 | 1.23 | **1-1** | 1-1 (12%), 1-0 (10%), 0-0 (10%) | 40/28/32 |
| Sweden | Tunisia | 1.17 | 1.05 | **1-0** | 1-0 (15%), 0-1 (12%), 0-0 (11%) | 42/23/35 |
| Netherlands | Sweden | 1.85 | 0.93 | **1-0** | 1-0 (13%), 2-0 (10%), 2-1 (9%) | 60/21/19 |
| Tunisia | Japan | 0.74 | 1.46 | **0-1** | 0-1 (16%), 0-0 (15%), 1-1 (12%) | 17/31/52 |
| Japan | Sweden | 1.72 | 0.93 | **1-0** | 1-0 (13%), 1-1 (10%), 2-0 (10%) | 56/24/21 |
| Tunisia | Netherlands | 0.62 | 1.75 | **0-1** | 0-1 (18%), 0-2 (13%), 0-0 (12%) | 8/26/65 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.50 | 0.90 | **1-0** | 1-0 (16%), 2-0 (11%), 0-1 (10%) | 54/19/27 |
| Iran | New Zealand | 1.67 | 0.71 | **1-0** | 1-0 (16%), 0-0 (13%), 1-1 (12%) | 59/29/12 |
| Belgium | Iran | 1.46 | 1.06 | **1-0** | 1-0 (14%), 2-0 (9%), 2-1 (9%) | 50/20/29 |
| New Zealand | Egypt | 0.73 | 1.38 | **0-1** | 0-1 (17%), 0-0 (16%), 1-1 (13%) | 16/33/52 |
| Egypt | Iran | 0.86 | 1.17 | **0-0** | 0-0 (15%), 0-1 (15%), 1-0 (12%) | 28/29/43 |
| New Zealand | Belgium | 0.76 | 1.92 | **0-1** | 0-1 (13%), 1-1 (13%), 0-0 (12%) | 8/30/61 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.41 | 0.47 | **1-0** | 1-0 (16%), 2-0 (16%), 3-0 (11%) | 81/15/4 |
| Saudi Arabia | Uruguay | 0.48 | 1.65 | **0-1** | 0-1 (22%), 0-2 (15%), 0-0 (14%) | 6/27/67 |
| Spain | Saudi Arabia | 2.27 | 0.49 | **1-0** | 1-0 (18%), 2-0 (16%), 3-0 (10%) | 81/15/4 |
| Uruguay | Cape Verde | 1.82 | 0.49 | **1-0** | 1-0 (21%), 2-0 (16%), 0-0 (10%) | 72/19/9 |
| Cape Verde | Saudi Arabia | 0.85 | 1.12 | **0-1** | 0-1 (16%), 0-0 (16%), 1-0 (12%) | 29/29/42 |
| Uruguay | Spain | 0.87 | 1.42 | **0-1** | 0-1 (15%), 0-0 (12%), 1-1 (11%) | 24/26/49 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.53 | 0.76 | **1-0** | 1-0 (18%), 2-0 (12%), 0-0 (11%) | 59/23/19 |
| Iraq | Norway | 0.71 | 1.44 | **0-1** | 0-1 (17%), 0-0 (15%), 1-1 (12%) | 15/31/54 |
| France | Iraq | 1.87 | 0.52 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (10%) | 72/19/8 |
| Norway | Senegal | 1.19 | 1.09 | **1-0** | 1-0 (15%), 0-0 (11%), 0-1 (11%) | 42/24/34 |
| Norway | France | 0.85 | 1.65 | **0-1** | 0-1 (14%), 1-1 (11%), 0-0 (11%) | 19/26/55 |
| Senegal | Iraq | 1.36 | 0.63 | **1-0** | 1-0 (19%), 0-0 (16%), 2-0 (12%) | 54/29/16 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.94 | 0.69 | **1-0** | 1-0 (17%), 2-0 (13%), 2-1 (10%) | 69/19/12 |
| Austria | Jordan | 1.51 | 0.94 | **1-0** | 1-0 (15%), 2-0 (10%), 0-0 (10%) | 53/22/25 |
| Argentina | Austria | 1.91 | 0.64 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (10%) | 67/21/12 |
| Jordan | Algeria | 0.88 | 1.37 | **1-1** | 1-1 (21%), 0-0 (20%), 0-1 (8%) | 14/51/35 |
| Algeria | Austria | 1.17 | 1.27 | **1-1** | 1-1 (12%), 0-1 (12%), 0-0 (12%) | 31/29/40 |
| Jordan | Argentina | 0.52 | 2.15 | **0-1** | 0-1 (14%), 0-2 (14%), 0-0 (12%) | 4/26/70 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.88 | 0.56 | **1-0** | 1-0 (18%), 2-0 (14%), 0-0 (10%) | 70/21/9 |
| Uzbekistan | Colombia | 0.62 | 1.55 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (12%) | 12/29/58 |
| Portugal | Uzbekistan | 1.71 | 0.67 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (11%) | 62/24/13 |
| Colombia | DR Congo | 1.70 | 0.51 | **1-0** | 1-0 (19%), 2-0 (14%), 0-0 (14%) | 65/26/8 |
| Colombia | Portugal | 1.22 | 1.07 | **1-0** | 1-0 (13%), 0-0 (12%), 1-1 (11%) | 41/28/32 |
| DR Congo | Uzbekistan | 0.87 | 1.07 | **0-1** | 0-1 (16%), 0-0 (15%), 1-0 (14%) | 32/28/41 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.36 | 0.84 | **1-0** | 1-0 (15%), 0-0 (14%), 1-1 (12%) | 48/29/23 |
| Ghana | Panama | 0.91 | 1.34 | **0-1** | 0-1 (16%), 0-0 (13%), 1-1 (12%) | 23/28/48 |
| England | Ghana | 1.93 | 0.48 | **1-0** | 1-0 (20%), 2-0 (16%), 0-0 (11%) | 73/22/5 |
| Panama | Croatia | 0.82 | 1.61 | **0-1** | 0-1 (14%), 0-0 (12%), 1-1 (12%) | 17/28/54 |
| Panama | England | 0.65 | 1.80 | **0-1** | 0-1 (15%), 0-0 (12%), 0-2 (12%) | 12/27/61 |
| Croatia | Ghana | 1.78 | 0.63 | **1-0** | 1-0 (20%), 2-0 (14%), 2-1 (10%) | 69/21/11 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Switzerland** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): D, E, F, G, I, J, K, L

**R32**  
- Ecuador 1-0 Türkiye → **Ecuador** (50% / 22% to win)
- France 1-0 Sweden → **France** (71% / 11% to win)
- South Korea 0-1 Switzerland → **Switzerland** (26% / 45% to win)
- Netherlands 0-0 Morocco → **Netherlands** (37% / 33% to win)
- Brazil 1-0 Japan → **Brazil** (50% / 22% to win)
- Germany 1-1 Norway → **Germany** (43% / 35% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (53% / 20% to win)
- England 1-0 Uzbekistan → **England** (60% / 9% to win)
- Portugal 1-0 Croatia → **Portugal** (52% / 28% to win)
- Spain 1-0 Austria → **Spain** (66% / 13% to win)
- Australia 1-0 Senegal → **Australia** (40% / 31% to win)
- Belgium 1-0 Algeria → **Belgium** (52% / 28% to win)
- Argentina 1-0 Uruguay → **Argentina** (55% / 21% to win)
- United States 0-1 Iran → **Iran** (31% / 42% to win)
- Canada 1-0 Egypt → **Canada** (39% / 32% to win)
- Colombia 1-0 Panama → **Colombia** (63% / 13% to win)

**R16**  
- Ecuador 0-1 France → **France** (27% / 44% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (27% / 45% to win)
- Brazil 1-0 Germany → **Brazil** (50% / 29% to win)
- Mexico 0-1 England → **England** (22% / 47% to win)
- Portugal 0-1 Spain → **Spain** (22% / 52% to win)
- Australia 1-1 Belgium → **Belgium** (26% / 43% to win)
- Argentina 1-0 Iran → **Argentina** (68% / 9% to win)
- Canada 0-1 Colombia → **Colombia** (14% / 57% to win)

**QF**  
- France 1-0 Netherlands → **France** (48% / 27% to win)
- Brazil 0-0 England → **England** (33% / 34% to win)
- Spain 1-0 Belgium → **Spain** (56% / 19% to win)
- Argentina 1-0 Colombia → **Argentina** (51% / 24% to win)

**SF**  
- France 1-0 England → **France** (38% / 36% to win)
- Spain 1-0 Argentina → **Spain** (37% / 37% to win)

**Final**  
- France 0-1 Spain → **Spain** (25% / 50% to win)

**Chalk champion: Spain** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): C, G, E, H, I, A, D, K

**R32**  
- Germany 3-0 Morocco → **Germany**
- France 1-4 Türkiye → **Türkiye**
- South Korea 2-0 Qatar → **South Korea**
- Netherlands 1-0 Scotland → **Netherlands**
- Brazil 3-1 Sweden → **Brazil**
- Ecuador 0-0 Iraq → **Ecuador** *(pens)*
- Mexico 0-0 Cape Verde → **Mexico** *(pens)*
- England 5-0 DR Congo → **England**
- Uzbekistan 1-2 Panama → **Panama**
- Uruguay 1-1 Algeria → **Uruguay** *(pens)*
- Paraguay 3-1 Curaçao → **Paraguay**
- Egypt 1-0 Czechia → **Egypt**
- Argentina 1-2 Spain → **Spain**
- Australia 1-3 Belgium → **Belgium**
- Switzerland 1-0 Iran → **Switzerland**
- Portugal 1-2 Senegal → **Senegal**

**R16**  
- Germany 3-1 Türkiye → **Germany**
- South Korea 2-3 Netherlands → **Netherlands**
- Brazil 0-1 Ecuador → **Ecuador**
- Mexico 2-4 England → **England**
- Panama 0-0 Uruguay → **Uruguay** *(pens)*
- Paraguay 2-0 Egypt → **Paraguay**
- Spain 0-1 Belgium → **Belgium**
- Switzerland 1-0 Senegal → **Switzerland**

**QF**  
- Germany 3-0 Netherlands → **Germany**
- Ecuador 0-0 England → **England** *(pens)*
- Uruguay 2-1 Paraguay → **Uruguay**
- Belgium 1-2 Switzerland → **Switzerland**

**SF**  
- Germany 2-0 England → **Germany**
- Uruguay 0-1 Switzerland → **Switzerland**

**Final**  
- Germany 0-2 Switzerland → **Switzerland**

**Sampled-scenario champion: Switzerland** 🏆
