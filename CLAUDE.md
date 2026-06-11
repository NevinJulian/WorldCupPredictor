# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An ML pipeline to predict international football matches and Monte-Carlo the **FIFA World Cup 2026**. The defining design choice (vs. most public WC models): it trains on **every international match since 1872** — friendlies and qualifiers included — not just World Cup finals. Read [PLAN.md](PLAN.md) for the full rationale; it is the source of truth for *why* the pipeline is shaped this way.

## Current status

**M0–M4 are complete and verified — the pipeline produces a real WC 2026 forecast.** What exists:
- End-to-end pipeline: `01_download` → raw CSVs; `02_build_features` → `data/processed/match_features.parquet` (**49,445 matches, 49 features** incl. as-of Elo, rolling form, rest/congestion, confederation/host flags, FIFA rank). Guard tests pass.
- **Models** (`src/wcpred/models.py`) scored via `walk_forward_tournaments` over 2010–2022 (normalized RPS, lower is better): Elo-logistic baseline (the bar, **0.2045**), Dixon-Coles goals (0.2147), GBM H/D/A isotonic-calibrated (**0.2030**), and their ensemble (**0.2036**). Metrics in `metrics.py` (RPS / log-loss / Brier / calibration).
- **Forecast** (`src/wcpred/forecast.py` → `scripts/08_forecast_2026.py`): Dixon-Coles scorelines reweighted to the ensemble's H/D/A, simulated through FIFA's real **Annex-C** R32 bracket (`config/annexc_r32.csv`). Output: per-team advance/round/title odds.
- A market sanity check (`scripts/market_check_2026.py` → `reports/market_check_2026.md`): the model over-concentrates on Spain + CONMEBOL sides vs the betting market — a known open question, not a bug.

**Next (optional):** M3-2 (XGBoost Poisson goals as a third, differently-failing ensemble component); investigate the CONMEBOL / Elo over-rating the market check surfaced. Roadmap in [PLAN.md](PLAN.md) §9.

## Workflow (branches, issues, PRs)

Every change is documented and goes through GitHub — more issues rather than fewer:
- **Issues + PRs + reviews + merges go through the GitHub MCP, NOT the `gh` CLI.** Use plain **git** only for local branch / commit / push.
- Open a GitHub issue for each change before starting. Work on one branch per issue (`feat/<issue#>-short-desc`), implement, run `pytest -q`, commit referencing the issue (`Closes #N`), push.
- `wc-builder` opens the PR (via the GitHub MCP) linking its issue, then stops. `pr-reviewer` runs the tests + the leakage checklist and merges (squash) only if green.
- CI (`.github/workflows/tests.yml`) runs `pytest` on every PR and is the hard gate — enable branch protection on `main` requiring the **tests** check so nothing red can merge.

## Commands

```powershell
# Setup (Windows venv already exists at .venv/; Python 3.12)
.venv\Scripts\activate
pip install -r requirements.txt

# Pipeline — run in order. Data is git-ignored, so 01 must run before anything else.
python scripts/01_download.py              # core data -> data/raw/ (no API key; add --advanced to scrape Transfermarkt)
python scripts/02_build_features.py        # -> data/processed/match_features.parquet (+ current_elo.csv, sample CSV)
python scripts/03_make_2026.py [--sims N]  # -> wc2026_group_fixtures.csv, wc2026_odds.csv (Elo-baseline forecast)
python scripts/08_forecast_2026.py [--sims N]  # -> wc2026_forecast_odds.csv (the real forecast: ensemble + Annex-C bracket)
python scripts/09_export_web.py [--sims-max N] # -> web/data/model_export.json (game-mode pairs, group fixtures, tournament odds + chalk; for the web UI)
# Static web UI (no framework/build): cd web && python -m http.server  -> http://localhost:8000/  (see web/README.md)
# scripts 04-07 fit/score the models -> data/processed/*_rps.json; gen_annexc_table.py rebuilds config/annexc_r32.csv (needs network)

# Tests (synthetic data, no network)
pytest -q
pytest tests/test_features.py::test_elo_is_as_of_no_leakage   # a single test

# Notebooks
jupyter lab notebooks/    # 01_data_overview -> 02_feature_signal -> 03_elo_baseline
```

There is no build, lint, or formatter configured. Tests are the only automated check.

## Architecture

Pipeline order (also in [src/wcpred/__init__.py](src/wcpred/__init__.py)):
`download -> clean -> elo (+features) -> datasets -> (models) -> tournament`

The package lives under `src/wcpred/` but is **not pip-installed** — there's no `pyproject.toml`/`setup.py`. Every script and the test file manually prepends `src` to `sys.path` before importing `wcpred`. Do the same for any ad-hoc script. Module paths anchor to the repo root via `wcpred.ROOT` (derived from `__file__`), so CWD doesn't matter.

Module map ([src/wcpred/](src/wcpred/)):
- `download.py` — fetches core tier (martj42 results/goalscorers/shootouts/former_names + FIFA ranking mirrors) per `config/sources.yaml`. `--advanced` delegates to `squad.py`.
- `clean.py` — `load_clean_results()` returns the canonical one-row-per-match frame (adds `played`, `result` H/D/A, `margin`, `total_goals`, `year`). `to_long()` builds the two-rows-per-match team-perspective view.
- `elo.py` — World Football Elo computed **in-house** (eloratings.net rules). `compute_elo()` returns matches with pre-match `elo_home`/`elo_away`/`elo_diff` plus post columns. K-factor comes from the `tournament` label via `k_for_tournament()`. Three knobs are tunable — `compute_elo(home_adv, k_scale, gd_strength)` — but their **defaults reproduce eloratings.net exactly**; tuning them on a large pre-2010 sample improved validation only microscopically and did **not** transfer to the WC backtest, so the defaults stand (negative result in `reports/elo_tuning.md`, via `scripts/elo_tuning.py`).
- `features.py` — `build_features(matches_with_elo, ranking, hosts)` assembles the wide modelling table. `feature_columns(df)` returns the model-input columns and is the **leakage gate** (drops targets, identifiers, and object columns).
- `datasets.py` — train/test construction. `time_split`, `tournament_holdout(df, year)`, `walk_forward_tournaments(...)`, `xy_outcome`, `xy_goals`.
- `tournament.py` — Monte-Carlo simulator for the 2026 format with FIFA's real **Annex-C** R32 bracket (so it requires the 12 groups A-L). `simulate_tournament(groups, model, n_sims)` returns per-team advance/round/title probabilities; `EloMatchModel` is the baseline stand-in. `load_annexc()`/`r32_matchups()` expose the bracket.
- `forecast.py` — assembles the real 2026 forecast match model (`ForecastMatchModel`: Dixon-Coles scorelines reweighted to the ensemble's H/D/A) and feeds it to `simulate_tournament`. The group stage uses the real in-data fixtures with host advantage; knockout pairs are scored neutral from a leakage-free per-team form snapshot.
- `confederations.py` / `squad.py` — team→confederation lookup; Transfermarkt squad-value/injury scraper (modern subset only).
- `webexport.py` — serialises the shipped forecast to `web/data/model_export.json` for a static web UI (game-mode neutral pairs, the 72 group fixtures, tournament odds at N∈{1k,10k,50k,100k} + the chalk bracket, Annex-C metadata). Reporting only — reads the fitted model, no refit. `build_forecast_model`'s `info` now also carries `neutral_matrices` (the pre-group-overwrite all-neutral matrices) so game mode can score every pair at a neutral venue.

### Non-negotiable invariants

**As-of / no-leakage by construction.** Every feature is the team's state *before* kickoff. Elo columns are pre-match (the rating attached to match *k* equals the post-match rating from match *k−1*). Rolling form in `features._rolling_team_features` always does `shift(1)` before any `.rolling()`/`.ewm()` window. Never introduce a feature that peeks at the current or future rows, and never add global normalisation that sees the whole dataset. Two tests guard this — `test_elo_is_as_of_no_leakage` and `test_build_features_form_is_as_of` — keep them green.

**Time-based evaluation only — never random split.** `datasets.py` exists to enforce this. The headline backtest is `tournament_holdout`/`walk_forward_tournaments`: to predict WC year *Y*, train only on matches strictly before *Y*'s finals. Primary metric is RPS (it respects H>D>A order), plus log-loss/Brier and calibration. The bar to beat is the pure-Elo baseline (PLAN.md §7).

### The two table shapes

The pipeline pivots between a **wide** table (one row per match, symmetric `home_*`/`away_*` columns + `*_diff` features, plus targets `home_score`/`away_score`/`result`) and an internal **long** view (two rows per match, one per team) used only to compute rolling form, which is then joined back. `features.py` does this round-trip via `match_id`; `clean.to_long()` is the standalone version.

### Pluggable match model

The simulator depends only on a duck-typed interface: `sample_scoreline(home, away, neutral, rng) -> (home_goals, away_goals)` for goals, plus `team_strength(team) -> float` (and an optional `strength_scale`) for the knockout shootout tiebreak. `EloMatchModel` is the baseline; `forecast.ForecastMatchModel` is the trained, ensemble-backed model — both satisfy the interface, so swapping them needs no simulator changes.

### Known caveats to respect

- **Team-name reconciliation is manual and scattered.** Data sources spell countries differently, so there are separate alias maps: `features._RANK_ALIASES` (ranking↔results), `scripts/03_make_2026.NAME_ALIASES` and `forecast.GROUP_ALIASES` (groups↔data), and `squad.TM_TEAMS` (Transfermarkt slugs). When adding a team or source, update the relevant map(s); unresolved names silently fall back to a median rating.
- **Advanced features (squad value/injuries) are modern-only and current-only.** They are for the 2026 layer and the "does this add signal?" experiment — never feed them into a pre-2007 backtest fold.
- **The 2026 knockout bracket is FIFA's real Annex-C slotting** (`config/annexc_r32.csv`, regenerated by `scripts/gen_annexc_table.py`; `simulate_tournament` therefore requires the 12 groups A-L). Residual approximations: knockout ties are played at neutral venues (host advantage is modelled only in the group stage), and drawn knockout ties resolve via a strength-weighted shootout.
- **`config/groups_2026.csv` matches the actual draw** — cross-checked against the real in-data fixtures (every team + intra-group pairing). Re-verify if the data source changes before publishing predictions.
