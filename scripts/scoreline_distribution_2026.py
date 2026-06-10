"""WC 2026 scoreline distributions + a deterministic chalk bracket (reporting only).

    python scripts/scoreline_distribution_2026.py

Reuses the shipped ForecastMatchModel (rating_sigma=0); no model/feature/fit change. Writes
reports/scoreline_distribution_2026.md with:
1. For every group fixture: the modal scoreline + top-3 scorelines with probabilities, plus
   E[goals] and P(H/D/A). These are read exactly from each fixture's score matrix (which every
   Monte-Carlo draw samples from), so the modal bucket equals the score-matrix argmax — the
   full-experiment result with no averaging.
2. A deterministic CHALK bracket (higher-win-probability team advances each tie, shown with its
   modal scoreline) next to the same single random sampled scenario, for contrast.
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import wcpred  # noqa: E402
from wcpred import clean, forecast  # noqa: E402

SCENARIO_SEED = 7   # the same realization shown in reports/forecast_2026.md


def main() -> int:
    matches = clean.load_clean_results()
    print("Building the forecast model...")
    model, sim_groups, display, info = forecast.build_forecast_model()
    gt = forecast.groups_by_name(sim_groups)
    team_group = {t: g for g, ts in gt.items() for t in ts}
    disp = lambda t: display.get(t, t)  # noqa: E731

    wc = matches[(matches["tournament"] == "FIFA World Cup") & (~matches["played"])]
    fixtures_by_group: dict = {}
    for _, r in wc.iterrows():
        h, a = r["home_team"], r["away_team"]
        if (h, a) in model.matrices:
            fixtures_by_group.setdefault(team_group[h], []).append((h, a))

    chalk = forecast.chalk_bracket(model, gt, fixtures_by_group)
    sampled = forecast.simulate_traced(model, gt, SCENARIO_SEED)

    as_of = str(matches.loc[matches["played"], "date"].max().date())
    L = [
        "# WC 2026 — scoreline distributions & the chalk bracket",
        "",
        f"*Reporting over the shipped ForecastMatchModel (v{wcpred.__version__}, rating_sigma=0, "
        f"per-confederation calibration on). As-of {as_of}; generated "
        f"{datetime.date.today().isoformat()}. Reporting only.*",
        "",
        "## 1. Group-fixture scoreline distributions",
        "",
        "Each fixture's scoreline probabilities are read **exactly** from its score matrix — the "
        "distribution every Monte-Carlo draw samples from — so the **modal** scoreline is the "
        "highest-probability bucket (equivalently the score-matrix argmax) and the top-3 are exact "
        "(no averaging). E[goals] and P(H/D/A) follow from the same matrix.",
        "",
    ]
    for g in sorted(fixtures_by_group):
        L += [f"**Group {g}**", "",
              "| Home | Away | E[H] | E[A] | Modal | Top-3 scorelines (prob) | P(H/D/A) |",
              "|--|--|--:|--:|:--:|--|:--:|"]
        for h, a in fixtures_by_group[g]:
            d = forecast.fixture_scoreline_distribution(model, h, a)
            mx, my = d["modal"]
            top = ", ".join(f"{x}-{y} ({p*100:.0f}%)" for (x, y), p in d["top"])
            L.append(f"| {disp(h)} | {disp(a)} | {d['e_home']:.2f} | {d['e_away']:.2f} | "
                     f"**{mx}-{my}** | {top} | {d['p_home']*100:.0f}/{d['p_draw']*100:.0f}/"
                     f"{d['p_away']*100:.0f} |")
        L.append("")

    L += ["## 2. Chalk bracket vs one sampled scenario", "",
          f"**Chalk champion: {disp(chalk['champion'])}**  ·  "
          f"**Sampled-scenario champion: {disp(sampled['champion'])}** (seed {SCENARIO_SEED})", ""]

    L += ["### 2a. Chalk bracket — the most-likely path, **NOT a probability**", "",
          "> Deterministic: group order by expected points, then the higher head-to-head win "
          "probability advances each tie, shown with that tie's **modal** scoreline. A single "
          "favourites-hold path — it does not represent how likely this exact run is.", "",
          f"8 best third-placed (groups): {', '.join(chalk['best_thirds'])}", ""]
    for rnd in ("R32", "R16", "QF", "SF", "Final"):
        L.append(f"**{rnd}**  ")
        for r, a, b, (mx, my), w, pa, pb in [t for t in chalk["bracket"] if t[0] == rnd]:
            L.append(f"- {disp(a)} {mx}-{my} {disp(b)} → **{disp(w)}** "
                     f"({pa*100:.0f}% / {pb*100:.0f}% to win)")
        L.append("")
    L.append(f"**Chalk champion: {disp(chalk['champion'])}** 🏆")
    L.append("")

    L += ["### 2b. One sampled scenario — a single random realization, **NOT the average**", "",
          f"> The same draw shown in `reports/forecast_2026.md` (seed {SCENARIO_SEED}). It "
          "samples actual scorelines (and shootouts on draws), so it diverges from the chalk path "
          "wherever an underdog wins.", "",
          f"8 best third-placed (groups): {', '.join(sampled['best_thirds'])}", ""]
    for rnd in ("R32", "R16", "QF", "SF", "Final"):
        L.append(f"**{rnd}**  ")
        for r, a, b, gh, ga, w, pens in [t for t in sampled["bracket"] if t[0] == rnd]:
            pens_s = " *(pens)*" if pens else ""
            L.append(f"- {disp(a)} {gh}-{ga} {disp(b)} → **{disp(w)}**{pens_s}")
        L.append("")
    L.append(f"**Sampled-scenario champion: {disp(sampled['champion'])}** 🏆")
    L.append("")

    out = ROOT / "reports" / "scoreline_distribution_2026.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Chalk champion: {disp(chalk['champion'])}; sampled champion: {disp(sampled['champion'])}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
