# World Cup 2026 forecast — web UI

A dependency-free static site (`index.html` + `app.js` + `styles.css`) that visualises the
forecast. It reads **`web/data/model_export.json`** (produced by `scripts/09_export_web.py`); no
framework, no build step, so it deploys as-is to GitHub Pages.

## Run locally

The page `fetch()`es the JSON, which browsers block over `file://`. Serve the folder over HTTP:

```bash
cd web
python -m http.server 8000
# then open http://localhost:8000/
```

Any static server works (`npx serve`, etc.) — the only requirement is HTTP, not `file://`.

## What's here

- **Game mode** (this release) — pick any two of the 48 teams; see the neutral-venue most-likely
  scoreline, the top-3 scorelines, a win/draw/loss bar, and expected goals, read from the first
  team's perspective. Pairs are stored unordered, so the app flips the scoreline and swaps
  win/loss when it finds the reverse ordering.
- **Tournament mode** — pick a simulation count (1k–100k); see title odds, 12 group cards with
  advance / placement and fixtures, and the deterministic chalk bracket. Click any match for a
  detail panel (top-3 scorelines, win/draw/loss, expected goals). Flags are bundled locally under
  `flags/` (MIT flag-icons) so they render offline and on Windows where emoji flags don't.

## Regenerating the data

```bash
python scripts/09_export_web.py        # rewrites web/data/model_export.json
```

The data contract (1128 game-mode pairs, the per-section fields the UI relies on) is guarded by
`tests/test_web_contract.py` — run `pytest -q` after regenerating.

## Live site

**https://NevinJulian.github.io/WorldCupPredictor/**

## Deploy (GitHub Pages)

`.github/workflows/pages.yml` publishes `web/` to Pages on every push to `main` (and on a manual
`workflow_dispatch`) via `upload-pages-artifact` + `deploy-pages`. **One-time setup:** in
*Settings → Pages*, set **Source = "GitHub Actions"**.

Notes:
- `web/.nojekyll` disables Jekyll, which otherwise strips files beginning with `_` — so the
  `_placeholder.svg` flag fallback would 404 without it.
- A project Pages site serves under `/<repo>/`, so every asset/data path in the site is **relative**
  (`data/model_export.json`, `flags/…`) — no absolute `/…` paths.
- Everything is static and `model_export.json` + the flags are committed, so no build runs.
