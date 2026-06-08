# ⚽ World Cup Predictor

An ML pipeline to predict international football matches and simulate the **FIFA World Cup
2026**. It trains on **every international match since 1872** (not just World Cup games), so
qualifiers and friendly form are part of the signal — the main gap in most public WC models.

> **Design & rationale:** see [`PLAN.md`](PLAN.md). Read it first — it explains *why* the
> pipeline looks the way it does (model goals → derive outcomes → simulate; validate against
> an Elo baseline with a time-based backtest).

## What's here (Milestone 0)

```
config/        sources.yaml (all data sources)  ·  groups_2026.csv (real final draw*)
src/wcpred/    download · clean · elo · features · squad · datasets · tournament
scripts/       01_download.py · 02_build_features.py · 03_make_2026.py
notebooks/     01_data_overview · 02_feature_signal · 03_elo_baseline
tests/         test_features.py (synthetic-data unit tests, no network)
```
\* transcribed from public reporting — verify vs fifa.com before publishing.

## Quickstart

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Download the core data (~a few MB; runs on YOUR machine, no API key needed)
python scripts/01_download.py                 # add --advanced to also scrape squad value/injuries

# 3. Build the feature table  ->  data/processed/match_features.parquet
python scripts/02_build_features.py

# 4. Explore: do the features actually carry signal?
jupyter lab notebooks/
```

Then work through the notebooks in order:
1. **01_data_overview** — sanity-check the data, quantify home advantage & draw rate, coverage over time.
2. **02_feature_signal** — the key one: does each feature (especially squad value / injuries)
   add predictive value *beyond Elo*? Mutual information, permutation importance, incremental log-loss.
3. **03_elo_baseline** — an Elo→outcome baseline with the RPS/log-loss/calibration harness you must beat.

## Status & next steps
Milestone 0 (foundation) is complete. See the roadmap in [`PLAN.md`](PLAN.md#9-roadmap) —
M1 is "run the signal check and prune features", then build the Dixon-Coles + Elo baselines.

## Data licensing / etiquette
Core match data is CC0 (martj42). The `--advanced` scraper hits Transfermarkt: it is rate-limited
and for personal/research use — keep request volume low and respect their terms.
