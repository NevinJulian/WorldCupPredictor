# Flags

The country flag SVGs in this directory are from **flag-icons** by Panayiotis Lipiridis,
distributed under the **MIT License** — https://github.com/lipis/flag-icons

Only the 48 flags needed by the World Cup 2026 UI are bundled here (4×3 variant), plus
`_placeholder.svg` (an original neutral fallback). They are vendored locally so the GitHub
Pages deploy is self-contained — no CDN, no CSP exceptions, works offline, and renders on
platforms where emoji flags don't (e.g. Windows browsers).

`flags.json` maps each of the 48 World Cup team display names to its flag's ISO-style code
(e.g. England → `gb-eng`, Curaçao → `cw`). It is the single source of truth shared by
`web/app.js` and the `tests/test_web_contract.py` coverage check.
