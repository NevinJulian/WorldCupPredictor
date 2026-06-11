"""Serialise the shipped 2026 forecast into one compact JSON for a static web UI.

This is a **reporting layer only** — it reads the already-fitted `ForecastMatchModel` and the
shipped `forecast`/`tournament` code; it never refits or alters the model, so the export
reflects the deployed model exactly. `scripts/09_export_web.py` is the thin CLI wrapper.

The payload (see `build_payload`) has four sections:
  * ``game_mode``    — every unordered pair of the 48 teams at a NEUTRAL venue: modal scoreline,
                       top-3 scorelines + probabilities, P(win/draw/win), expected goals.
  * ``group_stage``  — the 72 real group fixtures (host advantage where the real fixture has it),
                       same fields. These match `data/processed/forecast_2026.json` exactly.
  * ``tournament``   — per-team advance/R16/QF/SF/Final/title and per-group win/runner-up/3rd/
                       advance at N in {1000,10000,50000,100000} (the simulate_tournament-equivalent
                       `forecast.run_probabilities`, same seed), plus the deterministic chalk bracket.
  * ``metadata`` + ``structure`` — groups A-L, per-team confederation, the Annex-C slotting,
                       model_version, as-of, seed.

Probabilities are rounded to 4dp and expected goals to 3dp to keep the file compact.
"""
from __future__ import annotations

import datetime

import numpy as np

from . import forecast, tournament
from .confederations import confederation

PROB_DP = 4
EG_DP = 3
DEFAULT_LEVELS: tuple[int, ...] = (1000, 10000, 50000, 100000)
DEFAULT_SEED = 20260611                      # the canonical seed used by forecast_2026.json
REACH_COLS = ("advance", "R16", "QF", "SF", "Final", "title")


def _sl(xy) -> str:
    """A scoreline tuple -> 'home-away' string."""
    return f"{int(xy[0])}-{int(xy[1])}"


def _dist_json(d: dict) -> dict:
    """Serialise a `forecast.fixture_scoreline_distribution` dict compactly."""
    return {
        "modal": _sl(d["modal"]),
        "top": [[_sl(xy), round(p, PROB_DP)] for xy, p in d["top"]],
        "e_home": round(d["e_home"], EG_DP), "e_away": round(d["e_away"], EG_DP),
        "p_home": round(d["p_home"], PROB_DP), "p_draw": round(d["p_draw"], PROB_DP),
        "p_away": round(d["p_away"], PROB_DP),
    }


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
def game_mode_records(neutral_matrices: dict, teams_data: list[str], disp, top_k: int = 3) -> list[dict]:
    """Every unordered pair of the 48 teams at a neutral venue (display-name ordered).

    Reuses `forecast.fixture_scoreline_distribution` by wrapping the all-neutral matrices in a
    throwaway `ForecastMatchModel`, so the per-fixture maths is exactly the shipped reporting code.
    """
    gm = forecast.ForecastMatchModel(neutral_matrices, {})
    order = sorted(teams_data, key=lambda t: disp(t))
    out = []
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            if (a, b) not in neutral_matrices:        # defensive; every pair is precomputed
                continue
            d = forecast.fixture_scoreline_distribution(gm, a, b, top_k=top_k)
            out.append({"home": disp(a), "away": disp(b), **_dist_json(d)})
    return out


def group_stage_records(model, wc_fixtures, team_group: dict, disp, top_k: int = 3) -> list[dict]:
    """The 72 real group fixtures (true venue / host advantage), same fields as game mode.

    `wc_fixtures` is the data's unplayed FIFA-World-Cup fixtures frame (home_team/away_team in
    data spelling). Records are emitted only for fixtures present in the model's matrices.
    """
    out = []
    for _, r in wc_fixtures.iterrows():
        h, a = r["home_team"], r["away_team"]
        if (h, a) not in model.matrices:
            continue
        d = forecast.fixture_scoreline_distribution(model, h, a, top_k=top_k)
        out.append({"group": team_group.get(h, "?"), "home": disp(h), "away": disp(a), **_dist_json(d)})
    return out


def tournament_records(model, group_teams: dict, team_group: dict, disp,
                       levels=DEFAULT_LEVELS, seed: int = DEFAULT_SEED) -> dict:
    """Per-team reach odds and per-group placement at each N (same seed across levels).

    Uses `forecast.run_probabilities` (the simulate_tournament-equivalent that reuses the shipped
    `_simulate_group`/`_knockout` and additionally tallies 1st/2nd/3rd/4th placement). Returns
    ``{str(N): {"teams": [...], "groups": {g: [...]}}}``.
    """
    by_n: dict[str, dict] = {}
    for n in levels:
        reach, place = forecast.run_probabilities(model, group_teams, n, seed)
        teams = [{
            "team": disp(t), "group": team_group[t],
            **{c: round(reach[t][c] / n, PROB_DP) for c in REACH_COLS},
        } for t in sorted(reach, key=lambda t: -reach[t]["title"])]
        groups: dict[str, list] = {}
        for g, ts in group_teams.items():
            recs = [{
                "team": disp(t),
                "win": round(place[t][0] / n, PROB_DP), "runner_up": round(place[t][1] / n, PROB_DP),
                "third": round(place[t][2] / n, PROB_DP), "advance": round(reach[t]["advance"] / n, PROB_DP),
            } for t in ts]
            groups[g] = sorted(recs, key=lambda r: -r["advance"])
        by_n[str(n)] = {"teams": teams, "groups": groups}
    return by_n


def chalk_records(model, group_teams: dict, fixtures_by_group: dict, disp) -> dict:
    """The deterministic chalk bracket (NOT a probability) serialised with display names."""
    ch = forecast.chalk_bracket(model, group_teams, fixtures_by_group)
    bracket = [{
        "round": rnd, "home": disp(a), "away": disp(b), "modal": _sl(modal),
        "winner": disp(w), "p_home": round(pa, PROB_DP), "p_away": round(pb, PROB_DP),
    } for rnd, a, b, modal, w, pa, pb in ch["bracket"]]
    return {"champion": disp(ch["champion"]), "best_thirds": sorted(ch["best_thirds"]),
            "bracket": bracket}


def structure_records(group_teams: dict, teams_data: list[str], disp) -> dict:
    """Groups A-L (display names), each team's confederation, and the Annex-C slotting."""
    groups = {g: [disp(t) for t in ts] for g, ts in group_teams.items()}
    confeds = {disp(t): confederation(t) for t in teams_data}
    annexc = {
        "third_facing_winners": list(tournament._THIRD_FACING_WINNERS),
        "r32_bracket": [[list(x), list(y)] for x, y in tournament._R32_BRACKET],
        "n_combinations": len(tournament.load_annexc()),
    }
    return {"groups": groups, "confederations": confeds, "annexc": annexc}


# --------------------------------------------------------------------------- #
# Top-level assembly
# --------------------------------------------------------------------------- #
def build_payload(model, sim_groups, display, info, matches, *,
                  version: str, levels=DEFAULT_LEVELS, seed: int = DEFAULT_SEED,
                  generated: str | None = None) -> dict:
    """Assemble the full web-export payload from a built `ForecastMatchModel` and its context.

    `model, sim_groups, display, info` are exactly what `forecast.build_forecast_model` returns
    (so `info` must carry ``neutral_matrices``); `matches` is the cleaned match frame.
    """
    gt = forecast.groups_by_name(sim_groups)                 # group -> [data names]
    team_group = {t: g for g, ts in gt.items() for t in ts}
    teams_data = [t for ts in gt.values() for t in ts]
    disp = lambda t: display.get(t, t)                       # noqa: E731  data -> display name

    wc = matches[(matches["tournament"] == "FIFA World Cup") & (~matches["played"])]
    fixtures_by_group: dict = {}
    for _, r in wc.iterrows():
        h, a = r["home_team"], r["away_team"]
        if (h, a) in model.matrices:
            fixtures_by_group.setdefault(team_group[h], []).append((h, a))

    as_of = str(matches.loc[matches["played"], "date"].max().date())
    metadata = {
        "model": "ForecastMatchModel (Dixon-Coles scorelines reweighted to the GBM+DC ensemble "
                 "H/D/A, with per-confederation calibration), Annex-C bracket",
        "model_version": version, "as_of": as_of,
        "generated": generated or datetime.date.today().isoformat(),
        "confed_calibration": True, "rating_sigma": float(model.rating_sigma),
        "tournament_seed": seed, "tournament_levels": list(levels),
        "rounding": {"prob_dp": PROB_DP, "expected_goals_dp": EG_DP},
        "note": "Reporting export of the shipped v0.2.0 model (no refit). Game mode is neutral-venue; "
                "group stage uses each fixture's true venue and matches forecast_2026.json. Tournament "
                "odds reuse forecast.run_probabilities at one fixed seed across N (not averaged); the "
                "chalk bracket is the deterministic favourites-hold path, NOT a probability.",
    }
    return {
        "metadata": metadata,
        "structure": structure_records(gt, teams_data, disp),
        "game_mode": game_mode_records(info["neutral_matrices"], teams_data, disp),
        "group_stage": group_stage_records(model, wc, team_group, disp),
        "tournament": {
            "seed": seed, "levels": list(levels),
            "by_n": tournament_records(model, gt, team_group, disp, levels, seed),
            "chalk": chalk_records(model, gt, fixtures_by_group, disp),
        },
    }
