# World Cup Predictor — Architecture & Plan

This document is the design rationale. The short version: **model goals, derive
outcomes, simulate the bracket — and judge everything with a time-based backtest
against an Elo baseline.** If a model can't beat Elo out-of-sample, it isn't earning
its complexity.

---

## 1. Goal

Two linked prediction problems:

1. **Match model** — for any fixture (team A vs team B, date, venue), output a full
   probability distribution: P(win/draw/loss) *and* a scoreline distribution.
2. **Tournament model** — feed the 104 fixtures of WC 2026 through the match model and
   Monte-Carlo the bracket to get each team's probability of reaching each round / winning.

We build **both** a goals model and a direct outcome classifier and **ensemble** them
(the choice you picked). They fail in different ways, so blending them is a small, cheap
accuracy win and gives better-calibrated probabilities.

---

## 2. Why the reference projects fall short — and the fix

The repos you linked (e.g. *Fifa-WorldCup-Data-Analysis-1930-2026*) share three flaws:

| Flaw | Consequence | Our fix |
|---|---|---|
| Train on **World Cup matches only** (~900 rows, Wikipedia) | Tiny, biased sample; no form, no qualifiers | Train on **all internationals** (martj42, ~48k rows). Qualifiers/friendlies are already in there. |
| Predict outcome **directly from team identity** | Can't generalise to new matchups; leaks tournament-specific quirks | Predict from **as-of features** (Elo, form, rest…), never from raw team labels alone. |
| **Random** train/test split | Future leaks into the past → inflated accuracy | **Time-based** split + walk-forward backtest by tournament. |

The single highest-leverage change is the first one: switching the base table from
"World Cup matches" to "every international match" multiplies the data ~50× and bakes in
qualification + friendly form for free.

---

## 3. Data architecture

Three tiers (see `config/sources.yaml`):

**Core (no auth, full history 1872+):**
- `results.csv` — every international, with a `tournament` label (friendly / WC qualifier /
  Euro / Copa / WC finals…) and a `neutral` flag. This is the spine.
- `goalscorers.csv`, `shootouts.csv` — goal timings and shootout winners.
- FIFA Men's World Ranking (monthly since 1992) — merged as-of by date.

**Elo (computed in-house):** We don't download Elo; we *compute* World-Football-Elo from
`results.csv` chronologically (`src/wcpred/elo.py`). Benefits: zero dependency, exactly
as-of (no leakage), and we can tune the K-factors. Optional cross-check vs eloratings.net.

**Advanced (modern subset only):** squad market value + current injuries (Transfermarkt)
and squad player ratings (EA FC / SoFIFA). These only exist meaningfully from ~2007 and
are *current-only* for injuries. We use them for the **2026 prediction** and for the
"does this feature even help?" experiments — **not** for the deep historical backtest.
Being honest about coverage here matters; don't let a feature that only exists post-2007
silently break a 1990s backtest fold.

### The tidy table
`scripts/02_build_features.py` produces `data/processed/match_features.parquet`:
**one row per match**, with symmetric `home_*` / `away_*` feature columns and the targets
`home_score`, `away_score`, `result` (H/D/A). A team-perspective "long" view (two rows per
match) is generated internally for rolling-form computation, then joined back.

---

## 4. Features (all strictly as-of kickoff)

| Group | Features | Notes |
|---|---|---|
| Strength | `elo`, `elo_diff`, FIFA `rank`, `rank_points` | Elo diff is historically the single most predictive feature. |
| Form | last-5/last-10 points-per-game, goals for/against, **opponent- and recency-weighted** | Computed from prior matches only. Separate "competitive only" vs "all incl. friendlies". |
| Fatigue/context | `days_rest`, matches in last 30d, `is_neutral`, `is_host`, travel proxy | Host & neutral flags come straight from the data. |
| Competition | `match_weight` (friendly < qualifier < major) | Also used as the Elo K-factor. |
| Confederation | team confed, same-confed flag | Captures style/regional effects. |
| Advanced (modern) | squad market value, injury-adjusted value, avg age, #top-5-league players, avg FIFA rating | Coverage-gated; see tier above. |

**Leakage discipline** is enforced *by construction*: features are written as the team's
state **before** the match is played. `elo_home`/`elo_away` are pre-match; rolling windows
exclude the current row. There is no global normalisation that peeks at the future.

---

## 5. Modeling

### Component A — Goals model
Predict expected goals for each side, then turn that into outcome + scoreline probabilities.
Two interchangeable implementations:
- **Statistical (baseline):** Dixon-Coles / bivariate Poisson — team attack & defence
  strengths + home advantage, fit by weighted MLE with **time decay**. Strong, transparent,
  hard to beat. (`statsmodels` / custom likelihood.)
- **ML:** gradient-boosted regressors with a **Poisson objective** (XGBoost/LightGBM),
  one for `home_score`, one for `away_score`, on the full feature set.
Outcome probs come from a (Dixon-Coles-corrected) Poisson scoreline matrix; the same matrix
gives exact-score and over/under probabilities and feeds the tournament sim.

### Component B — Outcome classifier
Multiclass gradient boosting predicting **H/D/A** directly, optimised for log-loss, then
**probability-calibrated** (isotonic). Draws are the hard class; the classifier often
handles them better than a pure Poisson model.

### Ensemble
Blend A's derived H/D/A probabilities with B's. Start with a fixed weighted average tuned
on validation RPS; optionally upgrade to a small logistic **stacker**. Keep the goals model
as the source of truth for scorelines (the classifier doesn't produce them).

### Why not deep learning?
On tabular, ~48k-row football data, gradient boosting + Dixon-Coles consistently beats neural
nets in published comparisons. The 4080 is *not* the bottleneck here. Reach for the GPU only
for optional extensions: learned team/player **embeddings**, or a sequence model over a team's
recent matches feeding the ensemble. Treat those as v2 experiments, not the backbone.

---

## 6. Tournament simulation (2026 format)

`src/wcpred/tournament.py`, groups in `config/groups_2026.csv`:
- 12 groups of 4, round-robin (6 matches each). Rank by FIFA tiebreakers
  (points → GD → GF → head-to-head → …).
- Advance **top 2 of each group + the 8 best third-placed teams** → round of 32.
- Single elimination R32 → R16 → QF → SF → Final; extra time + penalties if level
  (sampled from the scoreline model + a shootout coin-flip weighted by strength).
- Run N≈50k simulations; aggregate to P(advance), P(reach SF/Final), P(win).

> The exact R32 slot for each third-placed team follows FIFA's Annex-C table (495 combos).
> The skeleton ships with the published winner/runner-up pairings and a documented
> placeholder for the third-place mapping — finalise it before trusting bracket odds.

---

## 7. Validation — the part that actually matters

**Never random-split.** Use:
1. **Tournament holdout / walk-forward:** to predict WC *Y*, train only on matches **before**
   that tournament started; score the tournament; repeat for 2010, 2014, 2018, 2022.
2. **Expanding-window time split** for the match model in general.

**Metrics:**
- 1X2: **Ranked Probability Score (RPS)** — primary, it respects order H>D>A — plus log-loss
  and Brier. **Calibration curves** (are "70%" wins actually ~70%?).
- Goals: Poisson deviance / MAE, and exact-score hit rate.

**Baselines you must beat (in order of toughness):**
1. Bookmaker odds (de-vigged) — the real bar; you likely won't beat it but measure the gap.
2. **Pure Elo logistic** — the practical bar. If your model doesn't beat this, simplify.
3. FIFA-ranking-only, and the naive base-rate (≈ home 45% / draw 27% / away 28%).

`notebooks/03_elo_baseline.ipynb` sets up baselines #2–#4 and the RPS/log-loss harness.

---

## 8. Hardware (RTX 4080 Super, 16 GB)

More than enough — and not the limiting factor. Boosting trains in seconds–minutes on CPU;
`tree_method="hist", device="cuda"` in XGBoost gives a modest speedup for hyperparameter
sweeps. The GPU genuinely earns its keep only for the optional embedding/sequence extensions
in §5. Don't choose deep learning *because* you have the card.

---

## 9. Roadmap

- [x] **M0 — Foundation (this session):** repo, data pipeline, Elo, features, 2026 config,
      sim skeleton, EDA notebooks.
- [ ] **M1 — Signal check:** run `02_feature_signal.ipynb`; keep features that add value over
      Elo; drop the rest. Decide if squad value/injuries are worth the scraping cost.
- [ ] **M2 — Baselines:** Dixon-Coles + Elo-logistic with the walk-forward backtest; record RPS.
- [ ] **M3 — ML match model:** XGBoost goals + outcome classifier; calibrate; ensemble; beat M2.
- [ ] **M4 — Tournament:** finalise Annex-C bracket; Monte-Carlo WC 2026; export odds.
- [ ] **M5 — (optional) GPU extensions:** team/player embeddings, sequence model.

---

## 10. Known limitations (be honest in any writeup)

- Football is high-variance; even a great model gives the favourite ~20–25% to win the
  whole thing. Calibration > point accuracy.
- Advanced features are modern-only and injuries are current-only — they help 2026, not 1994.
- The martj42 set has no lineups/xG; xG can be added later (FBref/understat) for the modern era.
- The 2026 group draw in `config/groups_2026.csv` is transcribed from public reporting —
  **verify against fifa.com before publishing predictions.**
