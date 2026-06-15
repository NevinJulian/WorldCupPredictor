"""Live grading of the WC-2026 forecast — running A/B over played matches (reports/live_grading.md).

    python scripts/grade_live_2026.py

For each played WC-2026 match, score the **pre-match** H/D/A for three variants on the same
fixtures: (1) the frozen pre-tournament forecast (group fixtures only), (2) the live result-only
model (xG off), (3) the live xG-adjusted model (xG on). Append the running RPS + a per-match table
to reports/live_grading.md.

As-of / leakage-free: matches are graded one matchday at a time; for matchday D the two live models
are rebuilt on data with every score on/after D blanked (`mask_future_scores`), so the match — and
everything later — is an unplayed fixture when the model that predicts it is fit. A match never
informs its own prediction. Run by `scripts/10_refresh.py` after each refresh; safe to run anytime
(writes an "awaiting matches" report when nothing is played yet).
"""
from __future__ import annotations

import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import clean, features, forecast, live_grading  # noqa: E402

PRETOURNAMENT = ROOT / "data" / "processed" / "forecast_2026_pretournament.json"
REPORT = ROOT / "reports" / "live_grading.md"


def main() -> int:
    matches = clean.load_clean_results()
    played = live_grading.played_wc_matches(matches)
    as_of = str(matches.loc[matches["played"], "date"].max().date())
    generated = datetime.date.today().isoformat()

    if played.empty:
        REPORT.parent.mkdir(exist_ok=True)
        REPORT.write_text(live_grading.render_report([], as_of, generated), encoding="utf-8")
        print("No WC-2026 matches played yet — wrote an 'awaiting matches' report.")
        print(f"Wrote {REPORT}")
        return 0

    ranking = features.load_fifa_ranking()
    frozen = live_grading.frozen_group_predictions(PRETOURNAMENT)
    records: list[dict] = []

    # One matchday at a time: rebuild both live variants as-of (data strictly before the matchday).
    for cutoff, day in played.groupby(played["date"], sort=True):
        masked = live_grading.mask_future_scores(matches, cutoff)
        model_off, _, disp_map, _ = forecast.build_forecast_model(masked, ranking, xg_adjustment=False)
        model_on, _, _, _ = forecast.build_forecast_model(masked, ranking, xg_adjustment=True)
        disp = lambda t: disp_map.get(t, t)   # noqa: E731  data -> display name

        for r in day.itertuples(index=False):
            h, a, actual = r.home_team, r.away_team, r.result
            fkey = (disp(h), disp(a))
            p_frozen = frozen.get(fkey)
            records.append({
                "date": pd.Timestamp(r.date).date().isoformat(),
                "stage": "group" if fkey in frozen else "KO",
                "home": disp(h), "away": disp(a),
                "score": f"{int(r.home_score)}-{int(r.away_score)}", "result": actual,
                "rps_frozen": live_grading.rps_hda(p_frozen, actual),
                "rps_off": live_grading.rps_hda(live_grading.prediction_hda(model_off, h, a), actual),
                "rps_on": live_grading.rps_hda(live_grading.prediction_hda(model_on, h, a), actual),
            })
        print(f"  graded {len(day)} match(es) on {pd.Timestamp(cutoff).date()} "
              f"(as-of model fit on data < {pd.Timestamp(cutoff).date()})")

    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(live_grading.render_report(records, as_of, generated), encoding="utf-8")
    s = live_grading.summarize(records)
    print(f"\nGraded {s['n']} matches ({s['n_group']} group). "
          f"Result-only {s['all_off']:.4f} vs xG-adjusted {s['all_on']:.4f} -> {s['lead']} leads.")
    print(f"Wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
