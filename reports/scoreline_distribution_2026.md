# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-16; generated 2026-06-17. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Czechia | South Africa | 1.31 | 0.79 | **1-0** | 1-0 (18%), 0-0 (14%), 1-1 (11%) | 50/28/22 |
| Mexico | South Korea | 1.74 | 0.92 | **1-0** | 1-0 (13%), 1-1 (11%), 2-0 (10%) | 56/26/18 |
| Mexico | Czechia | 1.94 | 0.90 | **1-1** | 1-1 (11%), 1-0 (11%), 2-0 (10%) | 58/26/16 |
| South Africa | South Korea | 0.68 | 1.40 | **0-1** | 0-1 (19%), 0-0 (14%), 0-2 (12%) | 18/27/55 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Switzerland | Bosnia and Herzegovina | 1.82 | 0.67 | **1-0** | 1-0 (17%), 2-0 (13%), 0-0 (10%) | 65/23/12 |
| Canada | Qatar | 2.30 | 0.78 | **1-0** | 1-0 (13%), 2-0 (12%), 2-1 (9%) | 72/18/10 |
| Canada | Switzerland | 1.38 | 1.27 | **1-1** | 1-1 (12%), 0-0 (10%), 0-1 (9%) | 37/28/35 |
| Bosnia and Herzegovina | Qatar | 1.34 | 0.99 | **1-0** | 1-0 (14%), 0-0 (13%), 1-1 (13%) | 46/30/24 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Morocco | 0.67 | 1.30 | **0-0** | 0-0 (17%), 0-1 (16%), 1-1 (12%) | 19/32/49 |
| Brazil | Haiti | 2.74 | 0.62 | **2-0** | 2-0 (12%), 1-0 (11%), 3-0 (10%) | 79/17/5 |
| Scotland | Brazil | 0.69 | 1.94 | **0-1** | 0-1 (12%), 0-0 (11%), 0-2 (11%) | 14/26/60 |
| Morocco | Haiti | 1.91 | 0.59 | **1-0** | 1-0 (18%), 2-0 (14%), 0-0 (10%) | 70/21/9 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Australia | 1.39 | 1.31 | **1-1** | 1-1 (11%), 0-1 (9%), 0-0 (9%) | 38/26/36 |
| Türkiye | Paraguay | 1.20 | 1.04 | **1-0** | 1-0 (13%), 0-0 (13%), 1-1 (11%) | 41/28/32 |
| United States | Türkiye | 1.75 | 1.23 | **1-1** | 1-1 (12%), 0-0 (8%), 1-0 (8%) | 45/27/28 |
| Paraguay | Australia | 0.87 | 1.20 | **0-0** | 0-0 (14%), 0-1 (14%), 1-0 (12%) | 29/28/43 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Ivory Coast | 1.88 | 0.87 | **1-0** | 1-0 (15%), 2-0 (11%), 2-1 (10%) | 64/20/16 |
| Ecuador | Curaçao | 2.12 | 0.52 | **1-0** | 1-0 (18%), 2-0 (15%), 3-0 (10%) | 77/17/6 |
| Curaçao | Ivory Coast | 0.70 | 1.93 | **0-1** | 0-1 (14%), 0-2 (12%), 0-0 (10%) | 12/23/65 |
| Ecuador | Germany | 1.05 | 1.35 | **1-1** | 1-1 (13%), 0-0 (12%), 0-1 (11%) | 28/30/41 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Sweden | 1.78 | 1.01 | **1-0** | 1-0 (12%), 1-1 (10%), 2-0 (9%) | 55/22/23 |
| Tunisia | Japan | 0.68 | 1.63 | **0-1** | 0-1 (17%), 0-0 (13%), 0-2 (12%) | 12/28/60 |
| Japan | Sweden | 1.69 | 0.94 | **1-0** | 1-0 (12%), 1-1 (12%), 0-0 (11%) | 53/28/19 |
| Tunisia | Netherlands | 0.66 | 1.78 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (11%) | 10/26/64 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Iran | 1.51 | 1.01 | **1-0** | 1-0 (14%), 2-0 (10%), 1-1 (9%) | 52/22/26 |
| New Zealand | Egypt | 0.71 | 1.45 | **0-1** | 0-1 (18%), 0-0 (14%), 1-1 (12%) | 14/30/56 |
| Egypt | Iran | 0.90 | 1.13 | **0-0** | 0-0 (15%), 0-1 (14%), 1-0 (12%) | 30/30/40 |
| New Zealand | Belgium | 0.78 | 1.89 | **1-1** | 1-1 (14%), 0-1 (12%), 0-0 (12%) | 9/32/59 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Saudi Arabia | 2.17 | 0.50 | **1-0** | 1-0 (17%), 2-0 (15%), 3-0 (10%) | 77/18/5 |
| Uruguay | Cape Verde | 1.74 | 0.50 | **1-0** | 1-0 (21%), 2-0 (15%), 0-0 (11%) | 70/20/10 |
| Cape Verde | Saudi Arabia | 0.86 | 1.07 | **0-0** | 0-0 (16%), 0-1 (15%), 1-0 (13%) | 30/30/40 |
| Uruguay | Spain | 0.81 | 1.47 | **0-1** | 0-1 (16%), 0-0 (12%), 1-1 (11%) | 20/27/53 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Iraq | 1.97 | 0.48 | **1-0** | 1-0 (20%), 2-0 (16%), 0-0 (10%) | 75/20/5 |
| Norway | Senegal | 1.30 | 1.02 | **1-0** | 1-0 (16%), 0-0 (11%), 1-1 (10%) | 47/24/29 |
| Norway | France | 0.87 | 1.61 | **1-1** | 1-1 (13%), 0-1 (13%), 0-0 (12%) | 19/30/51 |
| Senegal | Iraq | 1.42 | 0.63 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 56/29/15 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Austria | 1.90 | 0.63 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (11%) | 66/23/11 |
| Jordan | Algeria | 0.93 | 1.61 | **1-1** | 1-1 (12%), 0-0 (12%), 0-1 (12%) | 21/30/50 |
| Algeria | Austria | 1.21 | 1.28 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (10%) | 33/26/40 |
| Jordan | Argentina | 0.51 | 2.22 | **0-1** | 0-1 (14%), 0-2 (14%), 0-0 (11%) | 5/23/72 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | DR Congo | 1.94 | 0.53 | **1-0** | 1-0 (19%), 2-0 (15%), 0-0 (10%) | 72/21/7 |
| Uzbekistan | Colombia | 0.59 | 1.59 | **0-1** | 0-1 (18%), 0-0 (14%), 0-2 (13%) | 11/29/61 |
| Portugal | Uzbekistan | 1.78 | 0.65 | **1-0** | 1-0 (18%), 2-0 (13%), 0-0 (10%) | 66/21/12 |
| Colombia | DR Congo | 1.77 | 0.51 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (12%) | 69/22/9 |
| Colombia | Portugal | 1.26 | 1.05 | **1-0** | 1-0 (14%), 0-0 (11%), 1-1 (11%) | 43/26/31 |
| DR Congo | Uzbekistan | 0.83 | 1.11 | **0-1** | 0-1 (16%), 0-0 (15%), 1-0 (12%) | 29/28/43 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Croatia | 1.35 | 0.85 | **1-0** | 1-0 (14%), 0-0 (14%), 1-1 (11%) | 47/29/24 |
| Ghana | Panama | 0.90 | 1.36 | **0-1** | 0-1 (16%), 0-0 (13%), 1-1 (12%) | 22/28/50 |
| England | Ghana | 1.88 | 0.49 | **1-0** | 1-0 (19%), 2-0 (15%), 0-0 (12%) | 70/25/5 |
| Panama | Croatia | 0.85 | 1.57 | **0-1** | 0-1 (13%), 0-0 (12%), 1-1 (12%) | 19/29/52 |
| Panama | England | 0.63 | 1.86 | **0-1** | 0-1 (15%), 0-2 (13%), 0-0 (11%) | 11/24/64 |
| Croatia | Ghana | 1.75 | 0.64 | **1-0** | 1-0 (19%), 2-0 (14%), 2-1 (10%) | 67/21/11 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: France** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): A, B, D, E, G, I, K, L

**R32**  
- Germany 1-0 Czechia → **Germany** (60% / 16% to win)
- France 1-0 Türkiye → **France** (61% / 17% to win)
- South Korea 0-1 Switzerland → **Switzerland** (25% / 45% to win)
- Netherlands 0-0 Morocco → **Netherlands** (38% / 32% to win)
- Brazil 1-0 Japan → **Brazil** (51% / 20% to win)
- Ecuador 1-0 Senegal → **Ecuador** (45% / 26% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (48% / 24% to win)
- England 1-0 Uzbekistan → **England** (58% / 11% to win)
- Portugal 1-0 Croatia → **Portugal** (54% / 23% to win)
- Spain 1-0 Algeria → **Spain** (69% / 11% to win)
- United States 1-0 Bosnia and Herzegovina → **United States** (55% / 21% to win)
- Belgium 1-0 Norway → **Belgium** (46% / 30% to win)
- Argentina 1-0 Uruguay → **Argentina** (51% / 19% to win)
- Australia 1-0 Egypt → **Australia** (46% / 25% to win)
- Canada 0-0 Iran → **Iran** (30% / 38% to win)
- Colombia 1-0 Panama → **Colombia** (64% / 12% to win)

**R16**  
- Germany 0-1 France → **France** (30% / 47% to win)
- Switzerland 1-1 Netherlands → **Netherlands** (24% / 48% to win)
- Brazil 1-0 Ecuador → **Brazil** (46% / 27% to win)
- Mexico 0-1 England → **England** (20% / 50% to win)
- Portugal 0-1 Spain → **Spain** (24% / 48% to win)
- United States 1-1 Belgium → **Belgium** (20% / 51% to win)
- Argentina 1-0 Australia → **Argentina** (57% / 14% to win)
- Iran 0-1 Colombia → **Colombia** (21% / 49% to win)

**QF**  
- France 1-0 Netherlands → **France** (48% / 26% to win)
- Brazil 0-0 England → **England** (32% / 37% to win)
- Spain 1-1 Belgium → **Spain** (48% / 25% to win)
- Argentina 1-0 Colombia → **Argentina** (50% / 22% to win)

**SF**  
- France 0-0 England → **France** (36% / 34% to win)
- Spain 0-0 Argentina → **Argentina** (29% / 34% to win)

**Final**  
- France 0-1 Argentina → **Argentina** (23% / 48% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): C, E, D, G, H, I, A, F

**R32**  
- Ivory Coast 2-0 Morocco → **Ivory Coast**
- France 2-0 Tunisia → **France**
- South Korea 1-1 Canada → **South Korea** *(pens)*
- Sweden 2-1 Scotland → **Sweden**
- Brazil 0-0 Netherlands → **Brazil** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 5-0 Cape Verde → **Mexico**
- England 2-0 Senegal → **England**
- Uzbekistan 1-0 Panama → **Uzbekistan**
- Uruguay 1-1 Algeria → **Algeria** *(pens)*
- Paraguay 0-1 Ecuador → **Ecuador**
- Egypt 1-2 Czechia → **Czechia**
- Argentina 1-6 Spain → **Spain**
- United States 0-3 Belgium → **Belgium**
- Switzerland 1-1 Iran → **Iran** *(pens)*
- Portugal 3-2 Australia → **Portugal**

**R16**  
- Ivory Coast 0-1 France → **France**
- South Korea 3-2 Sweden → **South Korea**
- Brazil 0-0 Germany → **Germany** *(pens)*
- Mexico 1-5 England → **England**
- Uzbekistan 0-1 Algeria → **Algeria**
- Ecuador 1-0 Czechia → **Ecuador**
- Spain 3-0 Belgium → **Spain**
- Iran 0-0 Portugal → **Portugal** *(pens)*

**QF**  
- France 3-0 South Korea → **France**
- Germany 1-1 England → **England** *(pens)*
- Algeria 0-1 Ecuador → **Ecuador**
- Spain 0-2 Portugal → **Portugal**

**SF**  
- France 1-0 England → **France**
- Ecuador 0-1 Portugal → **Portugal**

**Final**  
- France 1-0 Portugal → **France**

**Sampled-scenario champion: France** 🏆
