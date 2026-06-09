# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An ML pipeline to predict international football matches and Monte-Carlo the **FIFA World Cup 2026**. The defining design choice (vs. most public WC models): it trains on **every international match since 1872** — friendlies and qualifiers included — not just World Cup finals. Read [PLAN.md](PLAN.md) for the full rationale; it is the source of truth for *why* the pipeline is shaped this way.

## Current status

**M0 (foundation) is complete and verified.** What exists:
- End-to-end pipeline: `01_download` → raw CSVs; `02_build_features` → `data/processed/match_features.parquet` (**49,445 matches, 49 features** incl. as-of Elo, rolling form, rest/congestion, confederation/host flags, FIFA rank). Guard tests pass.
- EDA notebooks 01–03 have been run (data overview, feature-signal, Elo baseline + RPS/calibration harness).
- 2026 groups encoded in `config/groups_2026.csv` (verify vs fifa.com); the Elo-baseline tournament sim runs.

**Next: M2 — baselines.** Build `src/wcpred/models.py` (Dixon-Coles goals + Elo-logistic outcome) and a metrics module (RPS / log-loss / Brier / calibration). Run `walk_forward_tournaments` over 2010–2022 and record the RPS to beat. Then M3: XGBoost goals + outcome → calibrate → ensemble. Roadmap in [PLAN.md](PLAN.md) §9.

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
- `elo.py` — World Football Elo computed **in-house** (eloratings.net rules). `compute_elo()` returns matches with pre-match `elo_home`/`elo_away`/`elo_diff` plus post columns. K-factor comes from the `tournament` label via `k_for_tournament()`.
- `features.py` — `build_features(matches_with_elo, ranking, hosts)` assembles the wide modelling table. `feature_columns(df)` returns the model-input columns and is the **leakage gate** (drops targets, identifiers, and object columns).
- `datasets.py` — train/test construction. `time_split`, `tournament_holdout(df, year)`, `walk_forward_tournaments(...)`, `xy_outcome`, `xy_goals`.
- `tournament.py` — Monte-Carlo simulator for the 2026 format. `EloMatchModel` is a stand-in match model; `simulate_tournament(groups, model, ratings, n_sims)` returns per-team advance/round/title probabilities.
- `confederations.py` / `squad.py` — team→confederation lookup; Transfermarkt squad-value/injury scraper (modern subset only).

### Non-negotiable invariants

**As-of / no-leakage by construction.** Every feature is the team's state *before* kickoff. Elo columns are pre-match (the rating attached to match *k* equals the post-match rating from match *k−1*). Rolling form in `features._rolling_team_features` always does `shift(1)` before any `.rolling()`/`.ewm()` window. Never introduce a feature that peeks at the current or future rows, and never add global normalisation that sees the whole dataset. Two tests guard this — `test_elo_is_as_of_no_leakage` and `test_build_features_form_is_as_of` — keep them green.

**Time-based evaluation only — never random split.** `datasets.py` exists to enforce this. The headline backtest is `tournament_holdout`/`walk_forward_tournaments`: to predict WC year *Y*, train only on matches strictly before *Y*'s finals. Primary metric is RPS (it respects H>D>A order), plus log-loss/Brier and calibration. The bar to beat is the pure-Elo baseline (PLAN.md §7).

### The two table shapes

The pipeline pivots between a **wide** table (one row per match, symmetric `home_*`/`away_*` columns + `*_diff` features, plus targets `home_score`/`away_score`/`result`) and an internal **long** view (two rows per match, one per team) used only to compute rolling form, which is then joined back. `features.py` does this round-trip via `match_id`; `clean.to_long()` is the standalone version.

### Pluggable match model

The simulator depends only on a duck-typed interface: any object with
`sample_scoreline(home, away, neutral, rng) -> (home_goals, away_goals)`.
`EloMatchModel` implements it today as the baseline. When the real ensembled goals+outcome model (PLAN.md §5) is trained, wrap it to satisfy this signature and pass it to `simulate_tournament` — no simulator changes needed.

### Known caveats to respect

- **Team-name reconciliation is manual and scattered.** Data sources spell countries differently, so there are three separate alias maps: `features._RANK_ALIASES` (ranking↔results), `make_2026.NAME_ALIASES` (groups↔Elo), and `squad.TM_TEAMS` (Transfermarkt slugs). When adding a team or source, update the relevant map(s); unresolved names silently fall back to a median rating.
- **Advanced features (squad value/injuries) are modern-only and current-only.** They are for the 2026 layer and the "does this add signal?" experiment — never feed them into a pre-2007 backtest fold.
- **The 2026 knockout bracket is approximate.** `tournament._knockout` Elo-seeds qualifiers into a standard bracket instead of FIFA's Annex-C third-place table (495 combos). Group-stage and `advance` probabilities are correct; deep-run/title odds are not final until the Annex-C mapping is implemented (PLAN.md §6).
- **`config/groups_2026.csv` is transcribed from public reporting** — verify against fifa.com before publishing predictions.
