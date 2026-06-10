# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.1.0, rating_sigma=0). As-of 2026-06-07; generated 2026-06-10. No model change.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | South Africa | 1.96 | 0.63 | **1-0** | 1-0 (18%), 2-0 (16%), 2-1 (12%) | 76/15/9 |
| South Korea | Czechia | 1.54 | 1.13 | **1-1** | 1-1 (13%), 1-0 (10%), 2-1 (9%) | 45/28/26 |
| Czechia | South Africa | 1.43 | 0.89 | **1-0** | 1-0 (17%), 1-1 (12%), 2-1 (11%) | 54/26/21 |
| Mexico | South Korea | 1.75 | 0.95 | **1-1** | 1-1 (13%), 1-0 (12%), 2-1 (11%) | 57/27/16 |
| Mexico | Czechia | 2.01 | 0.85 | **1-1** | 1-1 (14%), 1-0 (11%), 2-0 (11%) | 63/29/9 |
| South Africa | South Korea | 0.77 | 1.49 | **0-1** | 0-1 (16%), 1-1 (14%), 0-2 (11%) | 16/29/55 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Bosnia and Herzegovina | 2.15 | 0.66 | **2-0** | 2-0 (15%), 1-0 (14%), 2-1 (11%) | 75/16/9 |
| Qatar | Switzerland | 0.81 | 2.10 | **0-2** | 0-2 (12%), 0-1 (12%), 1-2 (11%) | 9/21/69 |
| Switzerland | Bosnia and Herzegovina | 1.95 | 0.70 | **1-0** | 1-0 (15%), 2-0 (14%), 2-1 (11%) | 70/21/10 |
| Canada | Qatar | 2.40 | 0.71 | **2-0** | 2-0 (13%), 1-0 (12%), 2-1 (11%) | 78/17/5 |
| Canada | Switzerland | 1.37 | 1.28 | **1-1** | 1-1 (15%), 0-0 (9%), 0-1 (9%) | 34/32/33 |
| Bosnia and Herzegovina | Qatar | 1.35 | 1.05 | **1-1** | 1-1 (14%), 1-0 (13%), 2-1 (10%) | 44/30/26 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Brazil | Morocco | 1.31 | 0.96 | **1-0** | 1-0 (17%), 2-1 (11%), 1-1 (11%) | 50/24/26 |
| Haiti | Scotland | 1.29 | 1.56 | **1-1** | 1-1 (12%), 1-2 (11%), 0-1 (10%) | 28/27/46 |
| Scotland | Morocco | 0.75 | 1.47 | **0-1** | 0-1 (15%), 1-1 (12%), 0-2 (12%) | 20/27/53 |
| Brazil | Haiti | 2.38 | 0.89 | **2-1** | 2-1 (14%), 2-0 (12%), 1-0 (11%) | 77/17/6 |
| Scotland | Brazil | 0.90 | 1.94 | **1-1** | 1-1 (11%), 0-1 (11%), 0-2 (11%) | 14/24/62 |
| Morocco | Haiti | 1.90 | 0.69 | **1-0** | 1-0 (17%), 2-0 (14%), 2-1 (12%) | 71/19/10 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Paraguay | 1.39 | 1.20 | **1-1** | 1-1 (12%), 0-1 (10%), 1-0 (9%) | 40/25/35 |
| Australia | Türkiye | 1.29 | 1.24 | **1-1** | 1-1 (13%), 0-1 (11%), 1-2 (9%) | 36/26/38 |
| United States | Australia | 1.35 | 1.47 | **1-1** | 1-1 (12%), 1-2 (9%), 0-1 (9%) | 34/25/41 |
| Türkiye | Paraguay | 1.21 | 1.13 | **1-0** | 1-0 (13%), 0-1 (12%), 1-1 (10%) | 41/22/37 |
| United States | Türkiye | 1.83 | 1.51 | **2-1** | 2-1 (9%), 1-1 (8%), 1-2 (8%) | 46/19/35 |
| Paraguay | Australia | 0.98 | 1.02 | **1-0** | 1-0 (16%), 0-1 (13%), 0-0 (12%) | 38/27/35 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Curaçao | 2.42 | 0.80 | **2-1** | 2-1 (13%), 2-0 (13%), 1-0 (12%) | 80/15/5 |
| Ivory Coast | Ecuador | 0.62 | 1.12 | **0-1** | 0-1 (25%), 0-0 (16%), 1-1 (11%) | 18/29/53 |
| Germany | Ivory Coast | 1.69 | 0.93 | **1-0** | 1-0 (17%), 2-1 (14%), 2-0 (12%) | 64/16/20 |
| Ecuador | Curaçao | 1.72 | 0.47 | **1-0** | 1-0 (25%), 2-0 (17%), 2-1 (12%) | 76/20/4 |
| Curaçao | Ivory Coast | 0.81 | 1.62 | **0-1** | 0-1 (15%), 1-1 (12%), 0-2 (12%) | 17/26/57 |
| Ecuador | Germany | 1.16 | 0.99 | **1-0** | 1-0 (16%), 1-1 (12%), 0-0 (11%) | 43/27/31 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Japan | 1.47 | 1.19 | **1-1** | 1-1 (13%), 1-0 (12%), 2-1 (11%) | 46/28/26 |
| Sweden | Tunisia | 1.28 | 1.21 | **1-0** | 1-0 (13%), 2-1 (10%), 0-1 (10%) | 44/19/37 |
| Netherlands | Sweden | 2.08 | 1.07 | **1-1** | 1-1 (11%), 2-1 (10%), 2-0 (9%) | 60/24/16 |
| Tunisia | Japan | 0.72 | 1.52 | **0-1** | 0-1 (16%), 1-1 (14%), 0-0 (12%) | 14/30/55 |
| Japan | Sweden | 2.04 | 0.94 | **1-1** | 1-1 (11%), 2-0 (10%), 2-1 (9%) | 61/24/15 |
| Tunisia | Netherlands | 0.73 | 1.70 | **0-1** | 0-1 (17%), 0-2 (13%), 1-2 (12%) | 11/24/64 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Egypt | 1.39 | 0.95 | **1-0** | 1-0 (15%), 2-0 (10%), 1-1 (10%) | 51/21/28 |
| Iran | New Zealand | 1.71 | 0.93 | **1-1** | 1-1 (14%), 1-0 (12%), 2-1 (10%) | 55/29/16 |
| Belgium | Iran | 1.57 | 1.18 | **1-0** | 1-0 (12%), 2-1 (12%), 1-1 (9%) | 52/19/29 |
| New Zealand | Egypt | 0.86 | 1.31 | **1-1** | 1-1 (15%), 0-1 (15%), 0-0 (13%) | 20/33/47 |
| Egypt | Iran | 0.94 | 1.25 | **0-1** | 0-1 (15%), 1-0 (11%), 1-1 (11%) | 30/25/46 |
| New Zealand | Belgium | 0.92 | 1.93 | **1-1** | 1-1 (12%), 0-1 (12%), 1-2 (12%) | 12/26/62 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Cape Verde | 2.30 | 0.58 | **2-0** | 2-0 (16%), 1-0 (15%), 2-1 (12%) | 82/15/3 |
| Saudi Arabia | Uruguay | 0.49 | 1.40 | **0-1** | 0-1 (25%), 0-0 (15%), 0-2 (14%) | 7/29/64 |
| Spain | Saudi Arabia | 2.16 | 0.56 | **1-0** | 1-0 (18%), 2-0 (17%), 2-1 (12%) | 81/15/4 |
| Uruguay | Cape Verde | 1.58 | 0.52 | **1-0** | 1-0 (26%), 2-0 (16%), 2-1 (12%) | 72/18/10 |
| Cape Verde | Saudi Arabia | 0.96 | 1.11 | **0-1** | 0-1 (15%), 1-1 (12%), 1-0 (12%) | 32/28/40 |
| Uruguay | Spain | 0.83 | 1.39 | **0-1** | 0-1 (15%), 1-1 (13%), 0-0 (11%) | 22/28/50 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Senegal | 1.62 | 0.94 | **1-0** | 1-0 (15%), 2-1 (13%), 1-1 (12%) | 58/24/18 |
| Iraq | Norway | 0.79 | 1.53 | **0-1** | 0-1 (16%), 1-1 (12%), 0-2 (12%) | 17/27/57 |
| France | Iraq | 1.80 | 0.56 | **1-0** | 1-0 (22%), 2-0 (16%), 2-1 (13%) | 75/19/6 |
| Norway | Senegal | 1.44 | 1.22 | **1-1** | 1-1 (12%), 1-0 (12%), 2-1 (11%) | 45/25/30 |
| Norway | France | 1.05 | 1.67 | **1-1** | 1-1 (15%), 0-1 (11%), 1-2 (11%) | 17/31/52 |
| Senegal | Iraq | 1.42 | 0.75 | **1-0** | 1-0 (17%), 1-1 (12%), 2-0 (12%) | 54/26/19 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Algeria | 1.75 | 0.72 | **1-0** | 1-0 (18%), 2-0 (13%), 2-1 (13%) | 68/22/10 |
| Austria | Jordan | 1.54 | 1.13 | **1-1** | 1-1 (11%), 1-0 (11%), 2-1 (10%) | 48/23/29 |
| Argentina | Austria | 1.79 | 0.68 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (12%) | 71/16/13 |
| Jordan | Algeria | 1.11 | 1.67 | **1-1** | 1-1 (14%), 0-1 (8%), 1-2 (8%) | 24/30/46 |
| Algeria | Austria | 1.20 | 1.22 | **1-1** | 1-1 (14%), 0-1 (12%), 0-0 (10%) | 33/29/38 |
| Jordan | Argentina | 0.70 | 2.06 | **1-1** | 1-1 (14%), 0-2 (12%), 0-1 (12%) | 5/29/67 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.51 | 0.65 | **1-0** | 1-0 (20%), 2-0 (13%), 1-1 (11%) | 62/25/13 |
| Uzbekistan | Colombia | 0.76 | 1.48 | **0-1** | 0-1 (16%), 1-1 (14%), 0-0 (12%) | 15/30/54 |
| Portugal | Uzbekistan | 1.58 | 0.78 | **1-0** | 1-0 (17%), 2-0 (12%), 1-1 (11%) | 59/24/16 |
| Colombia | DR Congo | 1.53 | 0.58 | **1-0** | 1-0 (23%), 2-0 (14%), 2-1 (11%) | 66/25/10 |
| Colombia | Portugal | 1.43 | 1.25 | **1-1** | 1-1 (13%), 1-0 (10%), 2-1 (10%) | 42/27/31 |
| DR Congo | Uzbekistan | 0.78 | 0.93 | **0-1** | 0-1 (19%), 0-0 (17%), 1-0 (14%) | 30/30/40 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.39 | 0.92 | **1-0** | 1-0 (14%), 1-1 (12%), 0-0 (10%) | 49/27/25 |
| Ghana | Panama | 0.91 | 1.61 | **0-1** | 0-1 (15%), 1-1 (13%), 1-2 (12%) | 17/26/57 |
| England | Ghana | 1.90 | 0.52 | **1-0** | 1-0 (19%), 2-0 (16%), 2-1 (11%) | 74/23/3 |
| Panama | Croatia | 0.99 | 1.65 | **1-1** | 1-1 (13%), 0-1 (12%), 1-2 (11%) | 19/28/53 |
| Panama | England | 0.82 | 1.72 | **1-1** | 1-1 (14%), 0-1 (13%), 0-2 (11%) | 14/29/57 |
| Croatia | Ghana | 1.81 | 0.69 | **1-0** | 1-0 (19%), 2-0 (14%), 2-1 (13%) | 71/19/10 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Spain** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, C, D, E, G, I, J, L

**R32**  
- Ecuador 1-0 Scotland → **Ecuador** (56% / 16% to win)
- France 1-1 Türkiye → **France** (58% / 19% to win)
- South Korea 1-1 Switzerland → **Switzerland** (20% / 52% to win)
- Netherlands 1-0 Morocco → **Netherlands** (47% / 31% to win)
- Brazil 1-0 Japan → **Brazil** (51% / 23% to win)
- Germany 1-1 Norway → **Germany** (46% / 30% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (53% / 21% to win)
- England 1-0 Senegal → **England** (53% / 21% to win)
- Portugal 1-1 Croatia → **Portugal** (49% / 26% to win)
- Spain 1-0 Austria → **Spain** (66% / 11% to win)
- United States 1-1 Algeria → **Algeria** (34% / 40% to win)
- Belgium 2-1 Czechia → **Belgium** (61% / 16% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 14% to win)
- Australia 1-1 Iran → **Iran** (33% / 37% to win)
- Canada 1-0 Egypt → **Canada** (45% / 29% to win)
- Colombia 1-1 Panama → **Colombia** (59% / 16% to win)

**R16**  
- Ecuador 0-1 France → **France** (22% / 49% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (22% / 45% to win)
- Brazil 2-1 Germany → **Brazil** (52% / 28% to win)
- Mexico 0-1 England → **England** (25% / 45% to win)
- Portugal 1-1 Spain → **Spain** (18% / 54% to win)
- Algeria 1-1 Belgium → **Belgium** (23% / 49% to win)
- Argentina 1-0 Iran → **Argentina** (66% / 10% to win)
- Canada 0-1 Colombia → **Colombia** (18% / 54% to win)

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

8 best third-placed (groups): E, G, K, F, J, A, D, C

**R32**  
- Ivory Coast 2-3 Türkiye → **Türkiye**
- France 1-1 Japan → **France** *(pens)*
- South Korea 0-3 Switzerland → **Switzerland**
- Netherlands 2-2 Brazil → **Netherlands** *(pens)*
- Morocco 1-0 Tunisia → **Morocco**
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 4-1 Scotland → **Mexico**
- England 2-0 DR Congo → **England**
- Uzbekistan 1-0 Panama → **Uzbekistan**
- Spain 2-0 Austria → **Spain**
- Paraguay 2-2 Algeria → **Paraguay** *(pens)*
- Egypt 1-2 Czechia → **Czechia**
- Argentina 2-0 Uruguay → **Argentina**
- United States 1-0 Belgium → **United States**
- Canada 1-1 Iran → **Iran** *(pens)*
- Portugal 3-0 Ecuador → **Portugal**

**R16**  
- Türkiye 0-1 France → **France**
- Switzerland 3-2 Netherlands → **Switzerland**
- Morocco 0-0 Germany → **Germany** *(pens)*
- Mexico 2-0 England → **Mexico**
- Uzbekistan 0-1 Spain → **Spain**
- Paraguay 1-1 Czechia → **Czechia** *(pens)*
- Argentina 0-0 United States → **Argentina** *(pens)*
- Iran 2-2 Portugal → **Portugal** *(pens)*

**QF**  
- France 2-2 Switzerland → **France** *(pens)*
- Germany 0-2 Mexico → **Mexico**
- Spain 2-0 Czechia → **Spain**
- Argentina 1-0 Portugal → **Argentina**

**SF**  
- France 1-0 Mexico → **France**
- Spain 3-2 Argentina → **Spain**

**Final**  
- France 1-2 Spain → **Spain**

**Sampled-scenario champion: Spain** 🏆
