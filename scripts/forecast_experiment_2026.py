"""Frozen WC 2026 forecast record from the shipped ForecastMatchModel (rating_sigma=0).

    python scripts/forecast_experiment_2026.py [--sims 50000]

Writes (frozen, reproducible — single fixed seed, no averaging of runs):
    reports/forecast_2026.md            — human-readable
    data/processed/forecast_2026.json   — machine-readable + metadata (as-of, N, seeds, version)

Contents: (1) Monte-Carlo probabilities per team (advance/R16/QF/SF/Final/title) with binomial
SE = sqrt(p(1-p)/N) and per-group placement; (2) expected goals + most-likely scoreline + P(H/D/A)
for each of the 72 fixtures (no simulation — read from the model's scoreline matrices); (3) ONE
sampled scenario with the full trace. A 2-3 seed title table is reported as a convergence check —
the runs are NOT averaged.
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

import wcpred  # noqa: E402
from wcpred import DATA_PROCESSED, clean, forecast, refresh  # noqa: E402

N_SIMS = 50000
SEED = 20260611             # the canonical probability seed (frozen)
SCENARIO_SEED = 7           # the one sampled realization
CONVERGENCE_SEEDS = (20260611, 11, 26)   # title-odds convergence check (NOT averaged)
REACH_COLS = ("advance", "R16", "QF", "SF", "Final", "title")


def _se(p, n):
    return float(np.sqrt(max(p * (1.0 - p), 0.0) / n))


def main(n_sims: int = N_SIMS) -> int:
    matches = clean.load_clean_results()
    print("Building the forecast model (ensemble fit + reweighted matrices)...")
    model, sim_groups, display, info = forecast.build_forecast_model()
    gt = forecast.groups_by_name(sim_groups)                 # group -> [data names]
    team_group = {t: g for g, ts in gt.items() for t in ts}
    disp = lambda t: display.get(t, t)                       # noqa: E731  data -> display name

    # --- (1) probabilities: one Monte Carlo at the canonical seed ---
    print(f"Monte-Carlo N={n_sims:,} seed={SEED} ...")
    reach, place = forecast.run_probabilities(model, gt, n_sims, SEED)
    teams_json = []
    for t in sorted(reach, key=lambda t: -reach[t]["title"]):
        probs = {c: reach[t][c] / n_sims for c in REACH_COLS}
        c1, c2, c3, c4 = (x / n_sims for x in place[t])
        teams_json.append({
            "team": disp(t), "group": team_group[t],
            **{c: round(probs[c], 5) for c in REACH_COLS},
            "se": {c: round(_se(probs[c], n_sims), 5) for c in REACH_COLS},
            "group_stage": {"win": round(c1, 5), "runner_up": round(c2, 5),
                            "third": round(c3, 5), "advance": round(probs["advance"], 5)},
        })

    # --- (2) expected group goals (no simulation) ---
    wc_fixtures = matches[(matches["tournament"] == "FIFA World Cup") & (~matches["played"])]
    fixtures_json = []
    for _, r in wc_fixtures.iterrows():
        h, a = r["home_team"], r["away_team"]
        if (h, a) not in model.matrices:
            continue
        fg = forecast.fixture_goal_model(model, h, a)
        x, y = fg["most_likely"]
        fixtures_json.append({
            "group": team_group.get(h, "?"), "home": disp(h), "away": disp(a),
            "e_home": round(fg["e_home"], 3), "e_away": round(fg["e_away"], 3),
            "most_likely": f"{x}-{y}",
            "p_home": round(fg["p_home"], 4), "p_draw": round(fg["p_draw"], 4),
            "p_away": round(fg["p_away"], 4),
        })

    # --- convergence check: title odds at 2-3 seeds (NOT averaged) ---
    conv = {s: {} for s in CONVERGENCE_SEEDS}
    conv[SEED] = {t: reach[t]["title"] / n_sims for t in reach}
    for s in CONVERGENCE_SEEDS:
        if s == SEED:
            continue
        rch, _ = forecast.run_probabilities(model, gt, n_sims, s)
        conv[s] = {t: rch[t]["title"] / n_sims for t in rch}
    conv_teams = [tj["team"] for tj in teams_json[:6]]
    data_to_disp = {t: disp(t) for t in reach}
    convergence_json = {dt: [round(conv[s][t], 5) for s in CONVERGENCE_SEEDS]
                        for t, dt in data_to_disp.items() if dt in conv_teams}

    # --- (3) one sampled scenario ---
    print(f"Recording one sampled scenario (seed={SCENARIO_SEED}) ...")
    sc = forecast.simulate_traced(model, gt, SCENARIO_SEED)
    scenario_json = {
        "seed": SCENARIO_SEED, "champion": disp(sc["champion"]),
        "best_thirds": sorted(sc["best_thirds"]),
        "groups": {g: {
            "standings": [{"team": disp(s["team"]), "pts": s["pts"], "gd": s["gd"], "gf": s["gf"]}
                          for s in d["table"]],
            "fixtures": [[disp(a), disp(b), gh, ga] for a, b, gh, ga in d["fixtures"]],
        } for g, d in sc["groups"].items()},
        "bracket": [{"round": rnd, "home": disp(a), "away": disp(b), "score": f"{gh}-{ga}",
                     "winner": disp(w), "shootout": pens}
                    for rnd, a, b, gh, ga, w, pens in sc["bracket"]],
    }

    as_of = str(matches.loc[matches["played"], "date"].max().date())
    payload = {
        "metadata": {
            "as_of": as_of, "generated": datetime.date.today().isoformat(),
            **refresh.played_counts(matches),   # matches_played + wc2026_matches_played (matchday loop)
            "n_sims": n_sims, "seed": SEED, "scenario_seed": SCENARIO_SEED,
            "convergence_seeds": list(CONVERGENCE_SEEDS),
            "model": "ForecastMatchModel (over-dispersed Dixon-Coles scorelines reweighted to the "
                     "GBM+DC ensemble H/D/A, with per-confederation calibration), Annex-C bracket",
            "model_version": wcpred.__version__, "rating_sigma": float(model.rating_sigma),
            "confed_calibration": True, "overdispersion": round(float(info["overdispersion"]), 3),
            "confed_offsets": {k: round(v, 4) for k, v in info["confed_offsets"].items()},
            "ensemble_weight_gbm": round(info["ensemble_weight"], 3),
            "n_group_fixtures": info["n_group_fixtures"], "n_pairs": info["n_pairs"],
            "se_formula": "binomial sqrt(p(1-p)/N)",
            "note": "A single fixed-seed Monte Carlo; runs are NOT averaged. The scenario is ONE "
                    "realization, not the mean. As of model v0.4.0 the Dixon-Coles strength "
                    "half-life is 5 years (reports/eval_and_decay.md), chosen on a broadened "
                    "competitive-internationals backtest; the forecast also applies the leakage-safe "
                    "per-confederation calibration (reports/confed_calibration_2026.md) and a "
                    "mean-preserving goals over-dispersion (reports/overdispersion_gate.md) — the "
                    "latter gives livelier scorelines at the same E[goals] and W/D/L.",
        },
        "teams": teams_json, "fixtures": fixtures_json,
        "convergence_title": convergence_json, "scenario": scenario_json,
    }
    out_json = DATA_PROCESSED / "forecast_2026.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    out_md = ROOT / "reports" / "forecast_2026.md"
    out_md.parent.mkdir(exist_ok=True)
    out_md.write_text(_render_md(payload), encoding="utf-8")

    print(f"\nChampion of the sampled scenario: {scenario_json['champion']}")
    print(f"Top title odds: " + ", ".join(f"{tj['team']} {tj['title']:.1%}" for tj in teams_json[:3]))
    print(f"Wrote {out_json}\nWrote {out_md}")
    return 0


def _render_md(p: dict) -> str:
    m = p["metadata"]
    L = [
        "# WC 2026 forecast — frozen record",
        "",
        f"*Model: {m['model']} (v{m['model_version']}, rating_sigma={m['rating_sigma']:.0f}). "
        f"As-of {m['as_of']}; generated {m['generated']}.*",
        "",
        f"**Monte Carlo:** N={m['n_sims']:,}, seed={m['seed']} (one run — **not** averaged). "
        f"Binomial SE = {m['se_formula']} (max ≈ {0.5/np.sqrt(m['n_sims'])*100:.2f} pp at p=0.5). "
        f"Ensemble weight w_gbm={m['ensemble_weight_gbm']}.",
        "",
        "## 1. Probabilities (per team)",
        "",
        "| Team | Grp | Advance | R16 | QF | SF | Final | Title (±SE) |",
        "|------|:--:|--:|--:|--:|--:|--:|--:|",
    ]
    for t in p["teams"]:
        L.append(f"| {t['team']} | {t['group']} | {t['advance']*100:.1f}% | {t['R16']*100:.1f}% | "
                 f"{t['QF']*100:.1f}% | {t['SF']*100:.1f}% | {t['Final']*100:.1f}% | "
                 f"{t['title']*100:.1f}% ±{t['se']['title']*100:.2f} |")
    L += ["", "*(Full per-cell SE in the JSON.)*", "",
          "### Group placement (P win / runner-up / 3rd / advance)", ""]
    by_group: dict = {}
    for t in p["teams"]:
        by_group.setdefault(t["group"], []).append(t)
    for g in sorted(by_group):
        L += [f"**Group {g}**", "", "| Team | Win | Runner-up | 3rd | Advance |", "|--|--:|--:|--:|--:|"]
        for t in sorted(by_group[g], key=lambda t: -t["group_stage"]["advance"]):
            gs = t["group_stage"]
            L.append(f"| {t['team']} | {gs['win']*100:.1f}% | {gs['runner_up']*100:.1f}% | "
                     f"{gs['third']*100:.1f}% | {gs['advance']*100:.1f}% |")
        L.append("")

    L += ["## 2. Expected group goals (no simulation)", "",
          "From each fixture's scoreline matrix: E[goals], the single most-likely scoreline, "
          "and P(home win / draw / away win).", ""]
    fx_by_group: dict = {}
    for fx in p["fixtures"]:
        fx_by_group.setdefault(fx["group"], []).append(fx)
    for g in sorted(fx_by_group):
        L += [f"**Group {g}**", "", "| Home | Away | E[H] | E[A] | Most likely | P(H/D/A) |",
              "|--|--|--:|--:|:--:|:--:|"]
        for fx in fx_by_group[g]:
            L.append(f"| {fx['home']} | {fx['away']} | {fx['e_home']:.2f} | {fx['e_away']:.2f} | "
                     f"**{fx['most_likely']}** | {fx['p_home']*100:.0f}/{fx['p_draw']*100:.0f}/"
                     f"{fx['p_away']*100:.0f} |")
        L.append("")

    L += ["## Convergence check — title odds at 3 seeds (not averaged)", "",
          "| Team | " + " | ".join(f"seed {s}" for s in m["convergence_seeds"]) + " |",
          "|--|" + "--:|" * len(m["convergence_seeds"])]
    for team, vals in p["convergence_title"].items():
        L.append(f"| {team} | " + " | ".join(f"{v*100:.1f}%" for v in vals) + " |")
    L.append("")

    sc = p["scenario"]
    L += ["## 3. One sampled scenario — a single realization, NOT the average",
          "",
          f"> **This is one random draw (seed {sc['seed']}), not a probability.** It shows what a "
          f"single tournament *could* look like. Champion: **{sc['champion']}**.", ""]
    L.append("### Group stage")
    L.append("")
    for g in sorted(sc["groups"]):
        d = sc["groups"][g]
        adv = ", ".join(s["team"] for s in d["standings"][:2])
        L += [f"**Group {g}** — through: {adv}", "",
              "| Pos | Team | Pts | GD | " + " | ".join(f"v {s['team']}" for s in d["standings"]) + " |",
              "|--:|--|--:|--:|" + "--:|" * len(d["standings"])]
        score = {}
        for a, b, gh, ga in d["fixtures"]:
            score[(a, b)] = f"{gh}-{ga}"
            score[(b, a)] = f"{ga}-{gh}"
        for i, s in enumerate(d["standings"]):
            cells = []
            for opp in d["standings"]:
                cells.append("—" if opp["team"] == s["team"] else score.get((s["team"], opp["team"]), ""))
            L.append(f"| {i+1} | {s['team']} | {s['pts']} | {s['gd']:+d} | " + " | ".join(cells) + " |")
        L.append("")
    L += [f"**8 best third-placed (groups):** {', '.join(sc['best_thirds'])}", "",
          "### Knockout bracket", ""]
    for rnd in ("R32", "R16", "QF", "SF", "Final"):
        ties = [t for t in sc["bracket"] if t["round"] == rnd]
        L.append(f"**{rnd}**  ")
        for t in ties:
            pens = " *(pens)*" if t["shootout"] else ""
            L.append(f"- {t['home']} {t['score']} {t['away']} → **{t['winner']}**{pens}")
        L.append("")
    L.append(f"**Champion: {sc['champion']}** 🏆")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    n = N_SIMS
    if "--sims" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sims") + 1])
    raise SystemExit(main(n))
