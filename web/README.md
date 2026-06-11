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
- **Tournament mode** — a labelled placeholder; advance/round/title odds and the chalk bracket
  arrive in the next release.

## Regenerating the data

```bash
python scripts/09_export_web.py        # rewrites web/data/model_export.json
```

The data contract (1128 game-mode pairs, the per-section fields the UI relies on) is guarded by
`tests/test_web_contract.py` — run `pytest -q` after regenerating.

## Deploy (GitHub Pages)

Serve the repository's `web/` directory (e.g. Pages → *Deploy from a branch*, folder `/web`, or a
Pages action). Because everything is static and `model_export.json` is committed, no build is needed.
