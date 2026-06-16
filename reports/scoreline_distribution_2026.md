# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-14; generated 2026-06-16. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Czechia | South Africa | 1.32 | 0.79 | **1-0** | 1-0 (18%), 0-0 (13%), 1-1 (10%) | 51/27/22 |
| Mexico | South Korea | 1.73 | 0.94 | **1-0** | 1-0 (13%), 1-1 (11%), 2-0 (10%) | 55/26/19 |
| Mexico | Czechia | 1.96 | 0.89 | **1-1** | 1-1 (11%), 1-0 (11%), 2-0 (10%) | 58/26/15 |
| South Africa | South Korea | 0.68 | 1.40 | **0-1** | 0-1 (19%), 0-0 (14%), 0-2 (12%) | 19/27/55 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Switzerland | Bosnia and Herzegovina | 1.79 | 0.66 | **1-0** | 1-0 (16%), 2-0 (12%), 0-0 (12%) | 63/27/10 |
| Canada | Qatar | 2.25 | 0.80 | **1-0** | 1-0 (12%), 2-0 (11%), 2-1 (9%) | 70/19/11 |
| Canada | Switzerland | 1.34 | 1.30 | **1-1** | 1-1 (12%), 0-0 (10%), 0-1 (10%) | 35/28/37 |
| Bosnia and Herzegovina | Qatar | 1.30 | 1.06 | **1-0** | 1-0 (14%), 0-0 (11%), 1-1 (11%) | 44/27/29 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Morocco | 0.67 | 1.34 | **0-1** | 0-1 (17%), 0-0 (16%), 0-2 (11%) | 19/29/51 |
| Brazil | Haiti | 2.79 | 0.62 | **2-0** | 2-0 (13%), 1-0 (11%), 3-0 (10%) | 81/14/5 |
| Scotland | Brazil | 0.66 | 1.95 | **0-0** | 0-0 (12%), 0-1 (12%), 0-2 (12%) | 12/28/61 |
| Morocco | Haiti | 1.97 | 0.58 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 73/18/8 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Australia | 1.37 | 1.32 | **1-1** | 1-1 (12%), 0-0 (9%), 0-1 (9%) | 37/27/37 |
| Türkiye | Paraguay | 1.21 | 1.04 | **1-0** | 1-0 (14%), 0-0 (12%), 0-1 (11%) | 42/26/32 |
| United States | Türkiye | 1.62 | 1.33 | **1-1** | 1-1 (12%), 0-0 (8%), 0-1 (8%) | 39/27/34 |
| Paraguay | Australia | 0.86 | 1.23 | **0-1** | 0-1 (15%), 0-0 (14%), 1-0 (12%) | 28/27/45 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Ivory Coast | 1.86 | 0.91 | **1-0** | 1-0 (15%), 2-0 (11%), 2-1 (10%) | 64/18/19 |
| Ecuador | Curaçao | 2.08 | 0.53 | **1-0** | 1-0 (18%), 2-0 (15%), 3-0 (9%) | 75/19/6 |
| Curaçao | Ivory Coast | 0.71 | 1.94 | **0-1** | 0-1 (15%), 0-2 (12%), 0-0 (9%) | 13/22/65 |
| Ecuador | Germany | 1.12 | 1.27 | **1-1** | 1-1 (13%), 0-0 (12%), 1-0 (10%) | 33/30/37 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Sweden | 1.75 | 1.01 | **1-0** | 1-0 (11%), 1-1 (11%), 0-0 (9%) | 53/26/22 |
| Tunisia | Japan | 0.71 | 1.58 | **0-1** | 0-1 (16%), 0-0 (13%), 0-2 (11%) | 15/28/57 |
| Japan | Sweden | 1.71 | 0.96 | **1-0** | 1-0 (12%), 1-1 (10%), 2-0 (10%) | 54/24/21 |
| Tunisia | Netherlands | 0.64 | 1.78 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (12%) | 9/27/64 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.50 | 0.86 | **1-0** | 1-0 (16%), 2-0 (11%), 0-0 (10%) | 54/23/23 |
| Iran | New Zealand | 1.72 | 0.72 | **1-0** | 1-0 (17%), 2-0 (12%), 0-0 (11%) | 62/24/13 |
| Belgium | Iran | 1.45 | 1.07 | **1-0** | 1-0 (14%), 2-0 (9%), 0-1 (9%) | 50/20/30 |
| New Zealand | Egypt | 0.73 | 1.39 | **0-1** | 0-1 (17%), 0-0 (15%), 1-1 (13%) | 16/32/52 |
| Egypt | Iran | 0.87 | 1.17 | **0-1** | 0-1 (15%), 0-0 (15%), 1-0 (12%) | 29/29/43 |
| New Zealand | Belgium | 0.72 | 1.98 | **0-1** | 0-1 (14%), 1-1 (12%), 0-2 (11%) | 6/29/64 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.46 | 0.48 | **1-0** | 1-0 (16%), 2-0 (16%), 3-0 (12%) | 83/11/5 |
| Saudi Arabia | Uruguay | 0.52 | 1.57 | **0-1** | 0-1 (20%), 0-0 (16%), 0-2 (13%) | 8/30/62 |
| Spain | Saudi Arabia | 2.31 | 0.49 | **1-0** | 1-0 (19%), 2-0 (16%), 3-0 (11%) | 83/12/5 |
| Uruguay | Cape Verde | 1.84 | 0.48 | **1-0** | 1-0 (22%), 2-0 (16%), 0-0 (10%) | 74/18/9 |
| Cape Verde | Saudi Arabia | 0.89 | 1.08 | **0-0** | 0-0 (16%), 0-1 (15%), 1-0 (13%) | 31/30/39 |
| Uruguay | Spain | 0.79 | 1.48 | **0-1** | 0-1 (15%), 0-0 (13%), 1-1 (12%) | 18/29/53 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.53 | 0.74 | **1-0** | 1-0 (18%), 2-0 (12%), 0-0 (11%) | 58/24/18 |
| Iraq | Norway | 0.74 | 1.43 | **0-1** | 0-1 (17%), 0-0 (14%), 1-1 (11%) | 17/29/54 |
| France | Iraq | 1.92 | 0.51 | **1-0** | 1-0 (21%), 2-0 (16%), 2-1 (9%) | 75/17/8 |
| Norway | Senegal | 1.20 | 1.09 | **1-0** | 1-0 (15%), 0-0 (11%), 0-1 (11%) | 43/24/33 |
| Norway | France | 0.86 | 1.61 | **0-1** | 0-1 (13%), 1-1 (12%), 0-0 (12%) | 19/28/53 |
| Senegal | Iraq | 1.37 | 0.62 | **1-0** | 1-0 (19%), 0-0 (16%), 2-0 (12%) | 55/29/16 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.96 | 0.66 | **1-0** | 1-0 (17%), 2-0 (13%), 2-1 (10%) | 70/20/10 |
| Austria | Jordan | 1.46 | 0.97 | **1-0** | 1-0 (14%), 0-0 (10%), 1-1 (10%) | 50/23/27 |
| Argentina | Austria | 1.87 | 0.65 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (10%) | 65/22/13 |
| Jordan | Algeria | 0.88 | 1.64 | **1-1** | 1-1 (13%), 0-0 (12%), 0-1 (12%) | 18/31/52 |
| Algeria | Austria | 1.21 | 1.27 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (10%) | 34/25/41 |
| Jordan | Argentina | 0.53 | 2.12 | **0-1** | 0-1 (14%), 0-2 (13%), 0-0 (12%) | 5/26/69 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.83 | 0.58 | **1-0** | 1-0 (17%), 2-0 (14%), 0-0 (11%) | 67/23/11 |
| Uzbekistan | Colombia | 0.61 | 1.59 | **0-1** | 0-1 (19%), 0-0 (14%), 0-2 (13%) | 12/27/61 |
| Portugal | Uzbekistan | 1.72 | 0.68 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (11%) | 63/23/14 |
| Colombia | DR Congo | 1.75 | 0.52 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (11%) | 68/22/10 |
| Colombia | Portugal | 1.22 | 1.09 | **1-0** | 1-0 (13%), 0-0 (12%), 1-1 (11%) | 41/27/33 |
| DR Congo | Uzbekistan | 0.87 | 1.10 | **0-1** | 0-1 (16%), 0-0 (14%), 1-0 (14%) | 32/26/43 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.31 | 0.90 | **1-0** | 1-0 (14%), 0-0 (13%), 1-1 (11%) | 45/27/28 |
| Ghana | Panama | 0.93 | 1.34 | **0-1** | 0-1 (16%), 0-0 (12%), 1-1 (11%) | 24/28/48 |
| England | Ghana | 1.93 | 0.49 | **1-0** | 1-0 (20%), 2-0 (16%), 0-0 (10%) | 73/20/6 |
| Panama | Croatia | 0.81 | 1.66 | **0-1** | 0-1 (15%), 0-0 (11%), 1-1 (11%) | 17/26/57 |
| Panama | England | 0.63 | 1.86 | **0-1** | 0-1 (15%), 0-2 (13%), 0-0 (11%) | 12/24/64 |
| Croatia | Ghana | 1.82 | 0.62 | **1-0** | 1-0 (20%), 2-0 (14%), 2-1 (11%) | 71/18/10 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: Spain** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, D, E, G, I, J, K, L

**R32**  
- Ecuador 1-0 Türkiye → **Ecuador** (44% / 29% to win)
- France 1-0 Egypt → **France** (67% / 12% to win)
- South Korea 0-1 Switzerland → **Switzerland** (26% / 44% to win)
- Netherlands 0-0 Morocco → **Netherlands** (37% / 31% to win)
- Brazil 1-1 Japan → **Brazil** (50% / 21% to win)
- Germany 1-1 Norway → **Germany** (48% / 31% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (49% / 25% to win)
- England 1-0 Uzbekistan → **England** (59% / 12% to win)
- Portugal 1-0 Croatia → **Portugal** (53% / 25% to win)
- Spain 1-0 Austria → **Spain** (65% / 11% to win)
- Australia 0-0 Senegal → **Australia** (38% / 33% to win)
- Belgium 1-0 Czechia → **Belgium** (58% / 21% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 17% to win)
- United States 0-1 Iran → **Iran** (28% / 44% to win)
- Canada 1-1 Algeria → **Algeria** (34% / 35% to win)
- Colombia 1-0 Panama → **Colombia** (65% / 12% to win)

**R16**  
- Ecuador 0-1 France → **France** (26% / 46% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (26% / 45% to win)
- Brazil 1-1 Germany → **Brazil** (49% / 23% to win)
- Mexico 0-1 England → **England** (17% / 51% to win)
- Portugal 0-1 Spain → **Spain** (21% / 49% to win)
- Australia 1-1 Belgium → **Belgium** (22% / 46% to win)
- Argentina 1-0 Iran → **Argentina** (63% / 10% to win)
- Algeria 0-1 Colombia → **Colombia** (20% / 53% to win)

**QF**  
- France 1-0 Netherlands → **France** (45% / 27% to win)
- Brazil 0-0 England → **England** (32% / 36% to win)
- Spain 1-1 Belgium → **Spain** (52% / 20% to win)
- Argentina 1-0 Colombia → **Argentina** (48% / 24% to win)

**SF**  
- France 0-0 England → **England** (35% / 37% to win)
- Spain 0-0 Argentina → **Argentina** (27% / 38% to win)

**Final**  
- England 0-1 Argentina → **Argentina** (21% / 48% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): C, E, G, I, A, D, F, K

**R32**  
- Ivory Coast 2-3 Türkiye → **Türkiye**
- France 2-0 Tunisia → **France**
- South Korea 1-1 Canada → **South Korea** *(pens)*
- Sweden 2-1 Scotland → **Sweden**
- Brazil 0-0 Netherlands → **Brazil** *(pens)*
- Germany 0-0 Iraq → **Germany** *(pens)*
- Mexico 3-1 Morocco → **Mexico**
- England 2-0 DR Congo → **England**
- Uzbekistan 1-0 Panama → **Uzbekistan**
- Spain 2-0 Algeria → **Spain**
- Paraguay 2-0 Ecuador → **Paraguay**
- Egypt 1-0 Czechia → **Egypt**
- Argentina 1-3 Uruguay → **Uruguay**
- Australia 1-3 Belgium → **Belgium**
- Switzerland 1-0 Iran → **Switzerland**
- Portugal 1-2 Senegal → **Senegal**

**R16**  
- Türkiye 1-4 France → **France**
- South Korea 3-1 Sweden → **South Korea**
- Brazil 0-1 Germany → **Germany**
- Mexico 2-3 England → **England**
- Uzbekistan 0-0 Spain → **Spain** *(pens)*
- Paraguay 2-0 Egypt → **Paraguay**
- Uruguay 0-1 Belgium → **Belgium**
- Switzerland 1-0 Senegal → **Switzerland**

**QF**  
- France 3-1 South Korea → **France**
- Germany 0-0 England → **England** *(pens)*
- Spain 3-1 Paraguay → **Spain**
- Belgium 1-2 Switzerland → **Switzerland**

**SF**  
- France 2-0 England → **France**
- Spain 1-0 Switzerland → **Spain**

**Final**  
- France 0-1 Spain → **Spain**

**Sampled-scenario champion: Spain** 🏆
