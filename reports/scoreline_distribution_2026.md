# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-20; generated 2026-06-21. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | Czechia | 1.95 | 0.87 | **1-1** | 1-1 (12%), 1-0 (11%), 2-0 (10%) | 58/28/14 |
| South Africa | South Korea | 0.67 | 1.37 | **0-1** | 0-1 (18%), 0-0 (15%), 0-2 (11%) | 17/29/53 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Switzerland | 1.35 | 1.32 | **1-1** | 1-1 (13%), 0-0 (10%), 0-1 (10%) | 34/29/37 |
| Bosnia and Herzegovina | Qatar | 1.33 | 1.08 | **1-0** | 1-0 (13%), 1-1 (11%), 0-0 (11%) | 44/27/29 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Brazil | 0.67 | 1.92 | **0-0** | 0-0 (12%), 0-1 (12%), 0-2 (11%) | 13/27/60 |
| Morocco | Haiti | 1.96 | 0.56 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 73/19/8 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Türkiye | 1.83 | 1.14 | **1-1** | 1-1 (12%), 0-0 (9%), 1-0 (8%) | 49/28/23 |
| Paraguay | Australia | 0.90 | 1.15 | **0-0** | 0-0 (15%), 0-1 (14%), 1-0 (13%) | 31/29/41 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Curaçao | Ivory Coast | 0.71 | 1.83 | **0-1** | 0-1 (14%), 0-2 (12%), 0-0 (11%) | 13/26/61 |
| Ecuador | Germany | 1.07 | 1.34 | **0-1** | 0-1 (12%), 1-1 (11%), 0-0 (11%) | 31/27/42 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Japan | Sweden | 1.81 | 0.94 | **1-0** | 1-0 (13%), 2-0 (10%), 1-1 (9%) | 58/22/20 |
| Tunisia | Netherlands | 0.65 | 1.85 | **0-1** | 0-1 (17%), 0-2 (13%), 0-0 (11%) | 9/24/67 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Iran | 1.45 | 1.08 | **1-0** | 1-0 (14%), 0-1 (9%), 2-0 (9%) | 49/20/30 |
| New Zealand | Egypt | 0.73 | 1.44 | **0-1** | 0-1 (18%), 0-0 (14%), 1-1 (12%) | 15/29/55 |
| Egypt | Iran | 0.85 | 1.20 | **0-1** | 0-1 (16%), 0-0 (14%), 1-0 (11%) | 27/28/45 |
| New Zealand | Belgium | 0.78 | 1.91 | **1-1** | 1-1 (13%), 0-1 (13%), 0-0 (11%) | 9/30/60 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Saudi Arabia | 2.16 | 0.51 | **1-0** | 1-0 (17%), 2-0 (15%), 3-0 (10%) | 76/18/6 |
| Uruguay | Cape Verde | 1.76 | 0.49 | **1-0** | 1-0 (21%), 2-0 (16%), 0-0 (11%) | 71/20/9 |
| Cape Verde | Saudi Arabia | 0.86 | 1.07 | **0-0** | 0-0 (16%), 0-1 (15%), 1-0 (13%) | 30/30/40 |
| Uruguay | Spain | 0.83 | 1.43 | **0-1** | 0-1 (15%), 0-0 (13%), 1-1 (11%) | 22/27/51 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Iraq | 2.02 | 0.49 | **1-0** | 1-0 (21%), 2-0 (17%), 2-1 (10%) | 78/15/6 |
| Norway | Senegal | 1.30 | 1.02 | **1-0** | 1-0 (16%), 0-0 (11%), 1-1 (10%) | 47/25/28 |
| Norway | France | 0.89 | 1.65 | **0-1** | 0-1 (13%), 1-1 (10%), 0-2 (10%) | 21/25/55 |
| Senegal | Iraq | 1.41 | 0.63 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 56/29/15 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Austria | 1.90 | 0.63 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (10%) | 66/22/11 |
| Jordan | Algeria | 0.91 | 1.64 | **1-1** | 1-1 (12%), 0-1 (12%), 0-0 (11%) | 20/29/51 |
| Algeria | Austria | 1.18 | 1.31 | **0-1** | 0-1 (13%), 1-1 (11%), 0-0 (10%) | 31/26/42 |
| Jordan | Argentina | 0.51 | 2.23 | **0-1** | 0-1 (14%), 0-2 (14%), 0-0 (11%) | 4/24/72 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | Uzbekistan | 1.68 | 0.69 | **1-0** | 1-0 (16%), 0-0 (12%), 2-0 (12%) | 60/26/14 |
| Colombia | DR Congo | 1.74 | 0.52 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (12%) | 67/24/9 |
| Colombia | Portugal | 1.29 | 1.01 | **1-0** | 1-0 (14%), 0-0 (12%), 1-1 (12%) | 44/29/27 |
| DR Congo | Uzbekistan | 0.89 | 1.05 | **0-0** | 0-0 (15%), 0-1 (15%), 1-0 (14%) | 32/28/39 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Ghana | 2.02 | 0.49 | **1-0** | 1-0 (21%), 2-0 (16%), 3-0 (10%) | 78/15/7 |
| Panama | Croatia | 0.87 | 1.59 | **0-1** | 0-1 (13%), 0-0 (12%), 1-1 (12%) | 20/28/52 |
| Panama | England | 0.58 | 1.94 | **0-1** | 0-1 (16%), 0-2 (13%), 0-0 (12%) | 7/26/67 |
| Croatia | Ghana | 1.67 | 0.68 | **1-0** | 1-0 (18%), 2-0 (12%), 0-0 (12%) | 62/25/13 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Argentina**  ·  **Sampled-scenario champion: Spain** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): B, D, G, H, I, J, K, L

**R32**  
- Ivory Coast 0-1 Paraguay → **Paraguay** (33% / 40% to win)
- France 1-0 Iran → **France** (61% / 15% to win)
- South Korea 0-1 Switzerland → **Switzerland** (25% / 47% to win)
- Netherlands 1-1 Brazil → **Brazil** (31% / 45% to win)
- Morocco 1-0 Japan → **Morocco** (43% / 29% to win)
- Germany 1-0 Senegal → **Germany** (57% / 22% to win)
- Mexico 1-0 Saudi Arabia → **Mexico** (63% / 12% to win)
- England 1-0 Uzbekistan → **England** (71% / 10% to win)
- Portugal 1-0 Croatia → **Portugal** (45% / 29% to win)
- Spain 1-0 Algeria → **Spain** (66% / 13% to win)
- United States 0-0 Canada → **United States** (38% / 32% to win)
- Belgium 0-1 Norway → **Belgium** (42% / 36% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 16% to win)
- Australia 1-0 Egypt → **Australia** (41% / 31% to win)
- Bosnia and Herzegovina 0-1 Austria → **Austria** (15% / 56% to win)
- Colombia 1-0 Panama → **Colombia** (69% / 9% to win)

**R16**  
- Paraguay 0-1 France → **France** (15% / 57% to win)
- Switzerland 1-1 Brazil → **Brazil** (21% / 52% to win)
- Morocco 0-0 Germany → **Germany** (36% / 36% to win)
- Mexico 0-1 England → **England** (17% / 50% to win)
- Portugal 1-1 Spain → **Spain** (19% / 50% to win)
- United States 1-1 Belgium → **Belgium** (22% / 48% to win)
- Argentina 1-0 Australia → **Argentina** (66% / 10% to win)
- Austria 0-1 Colombia → **Colombia** (24% / 55% to win)

**QF**  
- France 1-0 Brazil → **Brazil** (37% / 41% to win)
- Germany 0-1 England → **England** (31% / 45% to win)
- Spain 1-0 Belgium → **Spain** (55% / 19% to win)
- Argentina 1-0 Colombia → **Argentina** (51% / 25% to win)

**SF**  
- Brazil 0-1 England → **England** (31% / 41% to win)
- Spain 0-0 Argentina → **Argentina** (34% / 35% to win)

**Final**  
- England 0-1 Argentina → **Argentina** (26% / 48% to win)

**Chalk champion: Argentina** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): G, F, E, D, B, J, A, K

**R32**  
- Ivory Coast 2-2 Australia → **Australia** *(pens)*
- France 1-2 Netherlands → **Netherlands**
- South Korea 1-0 Bosnia and Herzegovina → **South Korea**
- Japan 1-5 Brazil → **Brazil**
- Morocco 0-0 Sweden → **Morocco** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 4-0 Ecuador → **Mexico**
- England 1-3 Colombia → **Colombia**
- Uzbekistan 1-0 Panama → **Uzbekistan**
- Spain 2-0 Austria → **Spain**
- Paraguay 2-2 Canada → **Paraguay** *(pens)*
- Egypt 1-2 Czechia → **Czechia**
- Argentina 2-0 Uruguay → **Argentina**
- United States 0-3 Belgium → **Belgium**
- Switzerland 1-1 Iran → **Iran** *(pens)*
- Portugal 4-0 Algeria → **Portugal**

**R16**  
- Australia 0-1 Netherlands → **Netherlands**
- South Korea 2-4 Brazil → **Brazil**
- Morocco 0-0 Germany → **Germany** *(pens)*
- Mexico 2-0 Colombia → **Mexico**
- Uzbekistan 0-1 Spain → **Spain**
- Paraguay 1-0 Czechia → **Paraguay**
- Argentina 3-1 Belgium → **Argentina**
- Iran 0-0 Portugal → **Portugal** *(pens)*

**QF**  
- Netherlands 2-1 Brazil → **Netherlands**
- Germany 1-3 Mexico → **Mexico**
- Spain 3-0 Paraguay → **Spain**
- Argentina 0-3 Portugal → **Portugal**

**SF**  
- Netherlands 0-2 Mexico → **Mexico**
- Spain 1-1 Portugal → **Spain** *(pens)*

**Final**  
- Mexico 0-2 Spain → **Spain**

**Sampled-scenario champion: Spain** 🏆
