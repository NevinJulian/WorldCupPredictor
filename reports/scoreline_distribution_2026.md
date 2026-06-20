# WC 2026 — scoreline distributions & the chalk bracket

*Reporting over the shipped ForecastMatchModel (v0.4.0, rating_sigma=0, per-confederation calibration on, goals over-dispersion 0.15). As-of 2026-06-19; generated 2026-06-20. Reporting only.*

## 1. Group-fixture scoreline distributions

Each fixture's scoreline probabilities are read **exactly** from its score matrix — the distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact (no averaging). E[goals] and P(H/D/A) follow from the same matrix.

**Group A**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Mexico | Czechia | 1.91 | 0.87 | **1-1** | 1-1 (13%), 0-0 (11%), 1-0 (11%) | 56/30/14 |
| South Africa | South Korea | 0.67 | 1.40 | **0-1** | 0-1 (19%), 0-0 (14%), 0-2 (12%) | 18/27/55 |

**Group B**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Canada | Switzerland | 1.36 | 1.33 | **1-1** | 1-1 (12%), 0-1 (10%), 0-0 (10%) | 35/27/38 |
| Bosnia and Herzegovina | Qatar | 1.35 | 1.04 | **1-0** | 1-0 (14%), 1-1 (12%), 0-0 (12%) | 46/28/27 |

**Group C**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Scotland | Brazil | 0.67 | 1.97 | **0-1** | 0-1 (13%), 0-2 (12%), 0-0 (11%) | 14/24/62 |
| Morocco | Haiti | 1.95 | 0.56 | **1-0** | 1-0 (19%), 2-0 (15%), 2-1 (10%) | 73/20/8 |

**Group D**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| United States | Türkiye | 1.82 | 1.17 | **1-1** | 1-1 (11%), 1-0 (8%), 0-0 (8%) | 48/27/25 |
| Paraguay | Australia | 0.94 | 1.10 | **0-0** | 0-0 (15%), 1-0 (14%), 0-1 (13%) | 33/29/38 |

**Group E**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Germany | Ivory Coast | 1.79 | 0.94 | **1-0** | 1-0 (14%), 2-0 (11%), 2-1 (10%) | 59/20/20 |
| Ecuador | Curaçao | 2.09 | 0.54 | **1-0** | 1-0 (18%), 2-0 (15%), 3-0 (9%) | 75/18/7 |
| Curaçao | Ivory Coast | 0.69 | 1.99 | **0-1** | 0-1 (15%), 0-2 (13%), 1-2 (9%) | 12/20/68 |
| Ecuador | Germany | 1.05 | 1.35 | **1-1** | 1-1 (13%), 0-0 (12%), 0-1 (11%) | 28/30/41 |

**Group F**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Netherlands | Sweden | 1.77 | 1.01 | **1-0** | 1-0 (11%), 1-1 (10%), 2-0 (9%) | 55/23/22 |
| Tunisia | Japan | 0.73 | 1.57 | **0-1** | 0-1 (16%), 0-0 (13%), 0-2 (11%) | 16/27/57 |
| Japan | Sweden | 1.70 | 0.96 | **1-0** | 1-0 (12%), 1-1 (11%), 2-0 (10%) | 54/25/21 |
| Tunisia | Netherlands | 0.63 | 1.82 | **0-1** | 0-1 (18%), 0-2 (13%), 0-0 (11%) | 9/24/67 |

**Group G**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Belgium | Iran | 1.48 | 1.05 | **1-0** | 1-0 (14%), 2-0 (9%), 2-1 (9%) | 51/21/29 |
| New Zealand | Egypt | 0.72 | 1.49 | **0-1** | 0-1 (19%), 0-0 (12%), 0-2 (12%) | 16/26/59 |
| Egypt | Iran | 0.89 | 1.14 | **0-0** | 0-0 (15%), 0-1 (14%), 1-0 (12%) | 29/30/41 |
| New Zealand | Belgium | 0.78 | 1.96 | **0-1** | 0-1 (13%), 0-2 (11%), 1-1 (11%) | 11/26/63 |

**Group H**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Spain | Saudi Arabia | 2.18 | 0.50 | **1-0** | 1-0 (18%), 2-0 (15%), 3-0 (10%) | 77/18/5 |
| Uruguay | Cape Verde | 1.77 | 0.48 | **1-0** | 1-0 (22%), 2-0 (16%), 0-0 (12%) | 71/21/8 |
| Cape Verde | Saudi Arabia | 0.90 | 1.03 | **0-0** | 0-0 (16%), 0-1 (15%), 1-0 (14%) | 33/29/38 |
| Uruguay | Spain | 0.79 | 1.46 | **0-1** | 0-1 (16%), 0-0 (13%), 1-1 (12%) | 19/29/52 |

**Group I**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| France | Iraq | 2.01 | 0.46 | **1-0** | 1-0 (21%), 2-0 (16%), 0-0 (10%) | 77/19/4 |
| Norway | Senegal | 1.24 | 1.11 | **1-0** | 1-0 (15%), 0-1 (11%), 0-0 (10%) | 44/22/34 |
| Norway | France | 0.88 | 1.64 | **0-1** | 0-1 (13%), 1-1 (11%), 0-0 (11%) | 20/26/54 |
| Senegal | Iraq | 1.42 | 0.63 | **1-0** | 1-0 (19%), 0-0 (15%), 2-0 (12%) | 57/28/15 |

**Group J**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Argentina | Austria | 1.91 | 0.62 | **1-0** | 1-0 (16%), 2-0 (13%), 0-0 (11%) | 67/23/10 |
| Jordan | Algeria | 0.89 | 1.65 | **1-1** | 1-1 (13%), 0-1 (12%), 0-0 (12%) | 18/30/52 |
| Algeria | Austria | 1.17 | 1.29 | **1-1** | 1-1 (12%), 0-1 (12%), 0-0 (12%) | 30/29/40 |
| Jordan | Argentina | 0.50 | 2.24 | **0-1** | 0-1 (15%), 0-2 (14%), 0-0 (11%) | 4/23/73 |

**Group K**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| Portugal | Uzbekistan | 1.72 | 0.68 | **1-0** | 1-0 (16%), 2-0 (12%), 0-0 (11%) | 62/25/13 |
| Colombia | DR Congo | 1.79 | 0.51 | **1-0** | 1-0 (20%), 2-0 (15%), 0-0 (11%) | 70/21/9 |
| Colombia | Portugal | 1.25 | 1.06 | **1-0** | 1-0 (13%), 0-0 (12%), 1-1 (11%) | 42/27/31 |
| DR Congo | Uzbekistan | 0.92 | 1.03 | **0-0** | 0-0 (15%), 1-0 (15%), 0-1 (15%) | 34/28/38 |

**Group L**

| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |
|--|--|--:|--:|:--:|--|:--:|
| England | Ghana | 1.98 | 0.48 | **1-0** | 1-0 (20%), 2-0 (16%), 0-0 (9%) | 75/19/6 |
| Panama | Croatia | 0.84 | 1.62 | **0-1** | 0-1 (14%), 0-0 (12%), 1-1 (12%) | 18/28/54 |
| Panama | England | 0.56 | 1.95 | **0-1** | 0-1 (16%), 0-2 (14%), 0-0 (12%) | 6/26/68 |
| Croatia | Ghana | 1.68 | 0.66 | **1-0** | 1-0 (18%), 2-0 (13%), 0-0 (12%) | 63/26/11 |

## 2. Chalk bracket vs one sampled scenario

**Chalk champion: Spain**  ·  **Sampled-scenario champion: Spain** (seed 7)

### 2a. Chalk bracket — the most-likely path, **NOT a probability**

> Deterministic: group order by expected points, then the higher head-to-head win probability advances each tie, shown with that tie's **modal** scoreline. A single favourites-hold path — it does not represent how likely this exact run is.

8 best third-placed (groups): B, E, F, G, H, I, J, K

**R32**  
- Ecuador 1-0 Sweden → **Ecuador** (51% / 23% to win)
- France 1-0 Iran → **France** (63% / 14% to win)
- South Korea 0-1 Switzerland → **Switzerland** (27% / 44% to win)
- Netherlands 1-1 Brazil → **Brazil** (22% / 49% to win)
- Morocco 1-0 Japan → **Morocco** (43% / 28% to win)
- Germany 1-0 Senegal → **Germany** (54% / 24% to win)
- Mexico 1-0 Ivory Coast → **Mexico** (49% / 22% to win)
- England 1-0 Uzbekistan → **England** (69% / 9% to win)
- Portugal 1-0 Croatia → **Portugal** (47% / 25% to win)
- Spain 1-0 Algeria → **Spain** (67% / 10% to win)
- United States 0-0 Canada → **Canada** (34% / 37% to win)
- Belgium 1-0 Saudi Arabia → **Belgium** (61% / 19% to win)
- Argentina 1-0 Uruguay → **Argentina** (54% / 17% to win)
- Australia 1-0 Egypt → **Australia** (40% / 33% to win)
- Bosnia and Herzegovina 0-1 Austria → **Austria** (12% / 57% to win)
- Colombia 1-0 Norway → **Colombia** (50% / 24% to win)

**R16**  
- Ecuador 0-1 France → **France** (31% / 45% to win)
- Switzerland 0-1 Brazil → **Brazil** (19% / 54% to win)
- Morocco 0-0 Germany → **Germany** (31% / 38% to win)
- Mexico 0-0 England → **England** (17% / 47% to win)
- Portugal 0-1 Spain → **Spain** (19% / 52% to win)
- Canada 1-1 Belgium → **Belgium** (19% / 49% to win)
- Argentina 1-0 Australia → **Argentina** (65% / 12% to win)
- Austria 0-1 Colombia → **Colombia** (20% / 53% to win)

**QF**  
- France 1-0 Brazil → **France** (39% / 37% to win)
- Germany 0-1 England → **England** (30% / 45% to win)
- Spain 1-0 Belgium → **Spain** (54% / 20% to win)
- Argentina 1-0 Colombia → **Argentina** (51% / 23% to win)

**SF**  
- France 0-1 England → **England** (34% / 39% to win)
- Spain 0-0 Argentina → **Spain** (36% / 33% to win)

**Final**  
- England 0-1 Spain → **Spain** (23% / 50% to win)

**Chalk champion: Spain** 🏆

### 2b. One sampled scenario — a single random realization, **NOT the average**

> The same draw shown in `reports/forecast_2026.md` (seed 7). It samples actual scorelines (and shootouts on draws), so it diverges from the chalk path wherever an underdog wins.

8 best third-placed (groups): E, D, G, B, K, J, A, I

**R32**  
- Ivory Coast 2-2 Australia → **Australia** *(pens)*
- France 2-0 Iran → **France**
- South Korea 1-0 Bosnia and Herzegovina → **South Korea**
- Sweden 1-2 Morocco → **Morocco**
- Brazil 0-0 Netherlands → **Brazil** *(pens)*
- Germany 0-0 Norway → **Germany** *(pens)*
- Mexico 3-3 Ecuador → **Ecuador** *(pens)*
- England 1-0 Colombia → **England**
- DR Congo 1-1 Panama → **Panama** *(pens)*
- Spain 1-1 Austria → **Spain** *(pens)*
- Paraguay 1-2 Canada → **Canada**
- Egypt 1-0 Czechia → **Egypt**
- Argentina 1-1 Uruguay → **Argentina** *(pens)*
- United States 2-5 Belgium → **Belgium**
- Switzerland 0-1 Algeria → **Algeria**
- Portugal 4-0 Senegal → **Portugal**

**R16**  
- Australia 0-0 France → **France** *(pens)*
- South Korea 1-3 Morocco → **Morocco**
- Brazil 0-1 Germany → **Germany**
- Ecuador 0-2 England → **England**
- Panama 1-4 Spain → **Spain**
- Canada 0-0 Egypt → **Egypt** *(pens)*
- Argentina 3-0 Belgium → **Argentina**
- Algeria 1-1 Portugal → **Portugal** *(pens)*

**QF**  
- France 0-1 Morocco → **Morocco**
- Germany 0-1 England → **England**
- Spain 1-1 Egypt → **Spain** *(pens)*
- Argentina 1-0 Portugal → **Argentina**

**SF**  
- Morocco 3-0 England → **Morocco**
- Spain 1-1 Argentina → **Spain** *(pens)*

**Final**  
- Morocco 0-1 Spain → **Spain**

**Sampled-scenario champion: Spain** 🏆
