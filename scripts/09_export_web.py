"""Export the shipped 2026 forecast to web/data/model_export.json for the static web UI.

    python scripts/09_export_web.py [--sims-max 100000]

Builds the shipped calibrated ForecastMatchModel (v0.2.0, confederation calibration on) once and
serialises it via `wcpred.webexport` — game mode (neutral pairs), the 72 group fixtures, the
tournament odds at N in {1000,10000,50000,100000} + the chalk bracket, and metadata. No model
changes; the group-stage fixtures match data/processed/forecast_2026.json exactly.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import wcpred  # noqa: E402
from wcpred import clean, forecast, webexport  # noqa: E402


def main(levels=webexport.DEFAULT_LEVELS) -> int:
    print("Loading matches & building the forecast model (ensemble fit + reweighted matrices)...")
    matches = clean.load_clean_results()
    model, sim_groups, display, info = forecast.build_forecast_model()
    print(f"  ensemble w_gbm={info['ensemble_weight']:.2f}, {info['n_group_fixtures']} group "
          f"fixtures, {info['n_pairs']} ordered pairs; confed offsets: {len(info['confed_offsets'])}")

    print(f"Monte-Carlo tournament at N={list(levels)} (seed={webexport.DEFAULT_SEED}) — this is the "
          f"slow part...")
    payload = webexport.build_payload(model, sim_groups, display, info, matches,
                                      version=wcpred.__version__, levels=levels)

    out = ROOT / "web" / "data" / "model_export.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")

    n_game = len(payload["game_mode"])
    n_group = len(payload["group_stage"])
    chalk = payload["tournament"]["chalk"]["champion"]
    top = payload["tournament"]["by_n"][str(max(levels))]["teams"][:3]
    size_kb = out.stat().st_size / 1024
    print(f"\nGame-mode pairs: {n_game}  |  group fixtures: {n_group}  |  chalk champion: {chalk}")
    print(f"Top title (N={max(levels)}): " + ", ".join(f"{t['team']} {t['title']*100:.1f}%" for t in top))
    print(f"Wrote {out} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    lv = webexport.DEFAULT_LEVELS
    if "--sims-max" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--sims-max") + 1])
        lv = tuple(n for n in webexport.DEFAULT_LEVELS if n <= cap) or (cap,)
    raise SystemExit(main(lv))
