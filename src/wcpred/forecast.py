"""First real WC 2026 forecast — outcome-reweighted Dixon-Coles Monte-Carlo.

The simulator needs, for every matchup it draws, a *scoreline* — so it has to use a goals
model (Dixon-Coles), not a bare 1X2 classifier. But Dixon-Coles is the weakest 1X2 view we
have (normalized RPS 0.2147 vs the ensemble's 0.2036). So we keep DC's *scoreline shape* but
**reweight each match's score matrix so its H/D/A marginals equal the calibrated ensemble
(GBM + DC) outcome probabilities** — the sim inherits the outcome edge while still sampling
real scorelines (needed for group-stage points/goal-difference and knockout draws).

Two layers of matchup:
  * **Group stage** — the data already carries the real 72 fixtures (with each game's true
    host/neutral flag), so they get canonical as-of features straight from `build_features`;
    their ensemble probs and DC matrices use the real venue (host advantage included).
  * **Knockout** — any two qualifiers can meet, so we score *every* ordered pair on neutral
    ground. Their feature rows are assembled arithmetically from a per-team current-form
    **snapshot** (built leakage-free, validated to reproduce `build_features` exactly).

As-of / no-leakage: everything is fit on `played_only` data and the snapshot is computed from
played history only. Deep-run / title odds remain PROVISIONAL — the knockout bracket seeds by
`team_strength` into a standard bracket rather than FIFA's Annex-C third-place table (M4-2).
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np
import pandas as pd

from . import clean, datasets, elo, features
from .confederations import confederation
from .models import ConfederationCalibrator, EnsembleModel
from .tournament import _knockout, _simulate_group, load_groups, r32_matchups

# Elo points -> natural log-odds (the standard Elo logistic), for the strength-shock tilt.
_ELO_LOGIT = math.log(10.0) / 400.0
# Furthest-round buckets: a team with reached-size <= lim counts toward that round.
_REACH_BUCKETS: tuple[tuple[str, int], ...] = (
    ("R16", 16), ("QF", 8), ("SF", 4), ("Final", 2), ("title", 1),
)

# groups_2026 display name -> data (martj42) spelling, for the few that differ. The rest
# (South Korea, Cape Verde, Curaçao, DR Congo, ...) already match the data spelling directly.
GROUP_ALIASES: dict[str, str] = {"Türkiye": "Turkey", "Czechia": "Czech Republic"}

# Team-level base form features; every home_*/away_*/_diff GBM column derives from these.
_BASE_FORM: tuple[str, ...] = (
    "form_ewm_ppg", "form_vs_elo_5",
    "form_ppg_5", "form_gf_5", "form_ga_5", "form_gd_5",
    "form_ppg_10", "form_gf_10", "form_ga_10", "form_gd_10",
)
_SNAP_DATE = pd.Timestamp("2027-01-01")    # strictly after every real fixture
_ELO_HOME_ADV = 100.0                       # eloratings home advantage (elo.DEFAULT_HOME_ADV)
# Blends DC net-strength (log-goal units) onto the Elo scale for the seeding/tiebreak strength.
ELO_PER_DC_UNIT = 100.0


# --------------------------------------------------------------------------- #
# Team-name resolution + current-form snapshot
# --------------------------------------------------------------------------- #
def resolve_team(team: str, known) -> str:
    """Map a groups_2026 display name to the data's spelling (direct hit first, then alias)."""
    if team in known:
        return team
    alias = GROUP_ALIASES.get(team)
    return alias if alias and alias in known else team


def _row_to_snap(r: pd.Series, side: str) -> dict:
    elo_col = "elo_home" if side == "home_" else "elo_away"
    confed_col = "home_confed" if side == "home_" else "away_confed"
    # rank columns are absent when no ranking file is supplied -> NaN (HGB handles it natively).
    snap = {"elo": float(r[elo_col]), "rank": r.get(side + "rank", np.nan),
            "rank_points": r.get(side + "rank_points", np.nan), "confed": r[confed_col]}
    for b in _BASE_FORM:
        snap[b] = r[side + b]
    return snap


def team_snapshot(played_matches: pd.DataFrame, ranking, teams, hosts) -> dict[str, dict]:
    """Per-team as-of feature snapshot (current form / elo / rank / confed), leakage-free.

    Appends one synthetic future-dated neutral fixture per *pair* of teams — each team appears
    in exactly one synthetic row, so the rolling-form `shift(1)` window for that row sees only
    the team's played history and never another synthetic row (no cross-contamination). Runs
    the real elo -> build_features pipeline on the played history + those fixtures and reads
    each team's team-level features off its single synthetic row. Reproduces `build_features`
    for a real fixture exactly (regression-tested).
    """
    teams = list(teams)
    if len(teams) % 2:
        raise ValueError("team_snapshot needs an even number of teams (each must appear once).")
    pairs = [(teams[i], teams[i + 1]) for i in range(0, len(teams), 2)]
    synth = pd.DataFrame([{
        "date": _SNAP_DATE, "home_team": h, "away_team": a, "home_score": np.nan,
        "away_score": np.nan, "tournament": "FIFA World Cup", "neutral": True, "played": False,
    } for h, a in pairs])

    with_elo, _ = elo.compute_elo(pd.concat([played_matches, synth], ignore_index=True))
    feat = features.build_features(with_elo, ranking, hosts=hosts)
    rows = feat[feat["date"] == _SNAP_DATE]

    snap: dict[str, dict] = {}
    for _, r in rows.iterrows():
        snap[r["home_team"]] = _row_to_snap(r, "home_")
        snap[r["away_team"]] = _row_to_snap(r, "away_")
    return snap


def assemble_pairs(snap: dict[str, dict], pairs) -> pd.DataFrame:
    """Build a model-input frame for `pairs` (neutral) arithmetically from the snapshot.

    Reproduces exactly the GBM columns `build_features` would emit for each neutral matchup:
    team-level home_*/away_* features straight from the snapshot, plus the pair-level
    `*_diff`, `elo_expected_home` (neutral -> adv 0) and `same_confed`. Validated to match the
    canonical builder to machine precision.
    """
    rows = []
    for h, a in pairs:
        sh, sa = snap[h], snap[a]
        eh, ea = sh["elo"], sa["elo"]
        c1, c2 = sh["confed"], sa["confed"]
        row = {
            "home_team": h, "away_team": a, "neutral": True,
            "elo_home": eh, "elo_away": ea, "elo_diff": eh - ea,
            "elo_expected_home": 1.0 / (1.0 + 10.0 ** (-(eh - ea) / 400.0)),
            "home_rank": sh["rank"], "away_rank": sa["rank"],
            "home_rank_points": sh["rank_points"], "away_rank_points": sa["rank_points"],
            "rank_diff": sh["rank"] - sa["rank"],
            "rank_points_diff": sh["rank_points"] - sa["rank_points"],
            # NaN == NaN is False in build_features, so an unknown confederation -> 0, not 1.
            "same_confed": int(pd.notna(c1) and pd.notna(c2) and c1 == c2),
        }
        for b in _BASE_FORM:
            row["home_" + b], row["away_" + b] = sh[b], sa[b]
            row[b + "_diff"] = sh[b] - sa[b]
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Outcome reweighting + the forecast match model
# --------------------------------------------------------------------------- #
def reweight_to_outcome(P: np.ndarray, target) -> np.ndarray:
    """Scale a DC scoreline matrix so its H/D/A marginals equal `target` = (pH, pD, pA).

    Multiplies all home-win cells by pH*/pH, draw cells by pD*/pD, away-win cells by pA*/pA,
    then renormalizes — preserving DC's conditional scoreline shape *within* each outcome class
    while adopting the better-calibrated ensemble 1X2 marginals. A class with zero DC mass (or
    a zero target) is passed through with factor 1 for that class.
    """
    G = P.shape[0]
    tl = np.tril(np.ones((G, G)), -1)    # home win: home goals > away goals
    dg = np.eye(G)                        # draw
    tu = np.triu(np.ones((G, G)), 1)      # away win: home goals < away goals
    pH, pD, pA = (P * tl).sum(), (P * dg).sum(), (P * tu).sum()
    tH, tD, tA = target
    sH = tH / pH if pH > 0 else 1.0
    sD = tD / pD if pD > 0 else 1.0
    sA = tA / pA if pA > 0 else 1.0
    R = P * (tl * sH + dg * sD + tu * sA)
    s = R.sum()
    return R / s if s > 0 else P


class ForecastMatchModel:
    """The 2026 match model: precomputed reweighted scoreline matrices + blended strength.

    Holds one reweighted score matrix per ordered ``(home, away)`` pair — group fixtures keyed
    with their real venue (host advantage), every other pair neutral — so `sample_scoreline`
    is a cheap table lookup + inverse-CDF draw. `team_strength` is an Elo backbone nudged by
    Dixon-Coles net strength; with ``strength_scale = 400`` it drives knockout seeding and the
    shootout tiebreak exactly like the Elo model. Satisfies the simulator's match-model
    interface, so it drops straight into `simulate_tournament`.
    """

    def __init__(self, matrices: dict, strengths: dict, strength_scale: float = 400.0,
                 fallback=None, rating_sigma: float = 0.0):
        self.matrices = matrices
        self.strengths = strengths
        self.strength_scale = strength_scale
        self._fallback = fallback   # a DixonColesModel, for pairs outside the precomputed set
        # Per-team rating-uncertainty SD in Elo points for the strength-shock dispersion lever.
        # 0 = off (the default): the WC backtest does not support it — the per-match model is
        # under-, not over-confident — see reports/sim_dispersion_2026.md.
        self.rating_sigma = float(rating_sigma)
        self._shock: dict | None = None

    def team_strength(self, team: str) -> float:
        return float(self.strengths.get(team, 0.0))

    def begin_tournament(self, rng) -> None:
        """Draw one correlated strength shock per team for this simulated tournament.

        With ``rating_sigma > 0`` each team's rating is perturbed by ``e_t ~ N(0, sigma^2)``
        ONCE per tournament — so a team sampled weak runs weak across all its matches — which
        widens the title distribution by construction. `simulate_tournament` calls this at the
        start of every simulation; at ``rating_sigma == 0`` it is a no-op.
        """
        self._shock = ({t: float(rng.normal(0.0, self.rating_sigma)) for t in self.strengths}
                       if self.rating_sigma > 0 else None)

    def _tilt(self, M: np.ndarray, delta: float) -> np.ndarray:
        """Shift non-draw mass between home and away by supremacy `delta` (nat log-odds)."""
        G = M.shape[0]
        tl = np.tril(np.ones((G, G)), -1)
        tu = np.triu(np.ones((G, G)), 1)
        pH, pA = (M * tl).sum(), (M * tu).sum()
        if pH <= 0 or pA <= 0:
            return M
        w = 1.0 / (1.0 + np.exp(-(np.log(pH / pA) + delta)))   # new home win-share of non-draw mass
        nd = pH + pA
        R = M * (1.0 + tl * (nd * w / pH - 1.0) + tu * (nd * (1.0 - w) / pA - 1.0))
        return R / R.sum()

    def sample_scoreline(self, home, away, neutral=True, rng=None) -> tuple[int, int]:
        rng = rng or np.random.default_rng()
        M = self.matrices.get((home, away))
        if M is None:   # defensive: every tournament pair is precomputed, so this is rare
            if self._fallback is not None:
                return self._fallback.sample_scoreline(home, away, neutral, rng)
            return int(rng.poisson(1.3)), int(rng.poisson(1.3))
        if self._shock is not None:   # strength-shock dispersion lever (off by default)
            delta = _ELO_LOGIT * (self._shock.get(home, 0.0) - self._shock.get(away, 0.0))
            if delta != 0.0:
                M = self._tilt(M, delta)
        cdf = np.cumsum(M.ravel())
        idx = int(np.searchsorted(cdf, rng.random() * cdf[-1]))
        ncols = M.shape[1]
        return idx // ncols, idx % ncols


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def build_forecast_model(
    matches: pd.DataFrame | None = None,
    ranking: pd.DataFrame | None = None,
    groups: pd.DataFrame | None = None,
    ensemble_kwargs: dict | None = None,
    rating_sigma: float = 0.0,
    confed_calibration: bool = True,
):
    """Fit the ensemble on all played data and assemble the 2026 `ForecastMatchModel`.

    ``rating_sigma`` (Elo) turns on the per-tournament strength-shock dispersion lever; it is
    0 (off) by default because the backtest does not support it (reports/sim_dispersion_2026.md).
    ``confed_calibration`` (ON by default) applies the per-confederation offset, which improves
    the walk-forward RPS and narrows the calibration gap (reports/confed_calibration_2026.md).

    Returns ``(model, sim_groups, display_to_data, info)``:
      * ``model``            — the ForecastMatchModel for `simulate_tournament`.
      * ``sim_groups``       — the groups frame with ``team`` set to the data spelling.
      * ``display_to_data``  — data-name -> display-name, to restore names on the output.
      * ``info``             — ensemble weight, pair/fixture counts, any unresolved names.
    """
    if matches is None:
        matches = clean.load_clean_results()
        if ranking is None:   # auto-load the ranking only on the real (non-injected) run
            ranking = features.load_fifa_ranking()
    if groups is None:
        groups = load_groups()

    with_elo, elo_model = elo.compute_elo(matches)
    ratings = elo_model.ratings
    feat = features.build_features(with_elo, ranking, hosts=features.HOSTS_2026)

    played = datasets.played_only(feat)
    ens = EnsembleModel(**(ensemble_kwargs or {})).fit(played)
    dc = ens.dc_
    calib = ConfederationCalibrator().fit(played) if confed_calibration else None

    g = groups.copy()
    g["team_data"] = g["team"].map(lambda t: resolve_team(t, ratings))
    teams = g["team_data"].tolist()
    unresolved = sorted(set(g.loc[~g["team_data"].isin(ratings), "team"]))

    # Per-team current snapshot from played history only (leakage-free, no contamination).
    snap = team_snapshot(matches[matches["played"]].copy(), ranking, teams, features.HOSTS_2026)

    team_confed = {t: confederation(t) for t in teams}

    # Knockout layer: every ordered pair on neutral ground, scored by the ensemble (then the
    # confederation offset, if on, before reweighting the Dixon-Coles scoreline matrix).
    pairs = [(a, b) for a in teams for b in teams if a != b]
    pair_probs = ens.predict_proba(assemble_pairs(snap, pairs))
    if calib is not None:
        pair_probs = calib.adjust(pair_probs, [team_confed[a] for a, _ in pairs],
                                  [team_confed[b] for _, b in pairs])
    matrices: dict[tuple[str, str], np.ndarray] = {}
    for (a, b), pr in zip(pairs, pair_probs):
        matrices[(a, b)] = reweight_to_outcome(dc.score_matrix(a, b, neutral=True), pr)

    # Group layer: the real fixtures override their neutral entries with the true venue
    # (host advantage). Both orderings are stored so the round-robin hits them either way.
    grp = feat[(feat["tournament"] == "FIFA World Cup") & (~feat["played"])
               & feat["home_team"].isin(teams) & feat["away_team"].isin(teams)].copy()
    n_group = 0
    if len(grp):
        grp_probs = ens.predict_proba(grp)
        if calib is not None:
            grp_probs = calib.adjust(grp_probs, grp["home_confed"].to_numpy(),
                                     grp["away_confed"].to_numpy())
        for (_, r), pr in zip(grp.iterrows(), grp_probs):
            h, a, neu = r["home_team"], r["away_team"], bool(r["neutral"])
            M = reweight_to_outcome(dc.score_matrix(h, a, neutral=neu), pr)
            matrices[(h, a)] = M
            matrices[(a, h)] = M.T   # reversed perspective = transpose of the score matrix
            n_group += 1

    # Blended strength: Elo backbone nudged by Dixon-Coles net strength (seeding/tiebreak only).
    default_elo = float(np.median(list(ratings.values()))) if ratings else elo.DEFAULT_RATING
    strengths = {t: float(ratings.get(t, default_elo)) + ELO_PER_DC_UNIT * dc.team_strength(t)
                 for t in teams}

    model = ForecastMatchModel(matrices, strengths, strength_scale=400.0, fallback=dc,
                               rating_sigma=rating_sigma)
    sim_groups = g.assign(team=g["team_data"])
    display_to_data = dict(zip(g["team_data"], g["team"]))
    info = {"ensemble_weight": float(ens.weight_), "n_pairs": len(pairs),
            "n_group_fixtures": n_group, "unresolved": unresolved,
            "confed_offsets": dict(calib.offsets_) if calib is not None else {}}
    return model, sim_groups, display_to_data, info


# --------------------------------------------------------------------------- #
# Reporting: Monte-Carlo probabilities + one traced scenario
# --------------------------------------------------------------------------- #
def groups_by_name(sim_groups: pd.DataFrame) -> dict[str, list[str]]:
    """{group letter -> [team, ...]} in the data's spelling, group order A-L."""
    return {g: sim_groups.loc[sim_groups["group"] == g, "team"].tolist()
            for g in sorted(sim_groups["group"].unique())}


def run_probabilities(model, group_teams: dict, n_sims: int, seed: int) -> tuple[dict, dict]:
    """Monte-Carlo the tournament `n_sims` times; return (reach_counts, place_counts).

    Reuses the shipped ``tournament._simulate_group`` / ``_knockout`` so these probabilities
    match ``simulate_tournament`` exactly, and additionally tallies group placement (finishing
    1st/2nd/3rd/4th). Counts are integers; divide by ``n_sims`` for probabilities. Honours the
    optional ``begin_tournament`` per-sim hook.
    """
    rng = np.random.default_rng(seed)
    begin = getattr(model, "begin_tournament", None)
    teams = [t for ts in group_teams.values() for t in ts]
    reach = {t: {k: 0 for k in ("advance", "R16", "QF", "SF", "Final", "title")} for t in teams}
    place = {t: [0, 0, 0, 0] for t in teams}   # counts of finishing 1st / 2nd / 3rd / 4th
    for _ in range(n_sims):
        if begin is not None:
            begin(rng)
        winners, runners, thirds = {}, {}, []
        for g, ts in group_teams.items():
            table = _simulate_group(ts, model, rng)
            for rank, s in enumerate(table):
                place[s["team"]][rank] += 1
            winners[g] = table[0]["team"]
            runners[g] = table[1]["team"]
            thirds.append({**table[2], "group": g})
        best = sorted(thirds, key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)[:8]
        third_by_group = {s["group"]: s["team"] for s in best}
        for t in set(winners.values()) | set(runners.values()) | set(third_by_group.values()):
            reach[t]["advance"] += 1
        for t, sz in _knockout(winners, runners, third_by_group, model, rng).items():
            for name, lim in _REACH_BUCKETS:
                if sz <= lim:
                    reach[t][name] += 1
    return reach, place


def fixture_goal_model(model, home: str, away: str) -> dict:
    """Expected goals, most-likely scoreline and P(H/D/A) for a fixture — no simulation.

    Reads the forecast model's precomputed (reweighted, real-venue) scoreline matrix directly.
    """
    M = model.matrices[(home, away)]
    rows = M.sum(axis=1)
    cols = M.sum(axis=0)
    g = np.arange(M.shape[0])
    x, y = np.unravel_index(int(M.argmax()), M.shape)
    return {
        "e_home": float(g @ rows), "e_away": float(g @ cols),
        "most_likely": (int(x), int(y)),
        "p_home": float(np.tril(M, -1).sum()), "p_draw": float(np.trace(M)),
        "p_away": float(np.triu(M, 1).sum()),
    }


def top_scorelines(M: np.ndarray, k: int = 3) -> list[tuple[tuple[int, int], float]]:
    """The k most-likely scorelines as ``[((home, away), prob), ...]``, probability-descending."""
    flat = M.ravel()
    ncols = M.shape[1]
    order = np.argsort(flat)[::-1][:k]
    return [((int(i // ncols), int(i % ncols)), float(flat[i])) for i in order]


def fixture_scoreline_distribution(model, home: str, away: str, top_k: int = 3) -> dict:
    """Exact scoreline distribution for a fixture — no simulation.

    Adds the modal scoreline and the top-k scorelines with probabilities to `fixture_goal_model`,
    all read from the fixture's score matrix. Because every Monte-Carlo draw samples from that
    matrix, these probabilities are exactly the N->infinity bucket frequencies; the modal scoreline
    equals the score-matrix argmax (i.e. `most_likely`).
    """
    fg = fixture_goal_model(model, home, away)
    top = top_scorelines(model.matrices[(home, away)], top_k)
    return {**fg, "modal": top[0][0], "top": top}


def expected_group_points(model, fixtures) -> dict[str, float]:
    """E[group points] per team from the fixtures' score matrices (deterministic, host-aware)."""
    pts: dict[str, float] = {}
    for home, away in fixtures:
        M = model.matrices[(home, away)]
        pH, pD, pA = float(np.tril(M, -1).sum()), float(np.trace(M)), float(np.triu(M, 1).sum())
        pts[home] = pts.get(home, 0.0) + 3 * pH + pD
        pts[away] = pts.get(away, 0.0) + 3 * pA + pD
    return pts


def chalk_bracket(model, group_teams: dict, fixtures_by_group: dict) -> dict:
    """The deterministic 'chalk' path — NOT a probability.

    Group order is by expected group points (host-aware); the top two of each group plus the 8
    third-placed teams with the most expected points qualify; Annex C fixes the R32; then in every
    knockout tie the team with the higher head-to-head win probability advances, shown with that
    tie's modal scoreline. Fully deterministic (no RNG).
    """
    epts_all, winners, runners, thirds_team, third_epts = {}, {}, {}, {}, {}
    for g, teams in group_teams.items():
        epts = expected_group_points(model, fixtures_by_group[g])
        epts_all.update(epts)
        order = sorted(teams, key=lambda t: epts[t], reverse=True)
        winners[g], runners[g], thirds_team[g] = order[0], order[1], order[2]
        third_epts[g] = epts[order[2]]
    best_groups = sorted(third_epts, key=lambda g: third_epts[g], reverse=True)[:8]
    third_by_group = {g: thirds_team[g] for g in best_groups}

    def advance(a, b):
        M = model.matrices[(a, b)]
        pa, pb = float(np.tril(M, -1).sum()), float(np.triu(M, 1).sum())
        (x, y), _ = top_scorelines(M, 1)[0]
        return (a if pa >= pb else b), (x, y), pa, pb

    bracket, field = [], []
    for a, b in r32_matchups(winners, runners, third_by_group):
        w, modal, pa, pb = advance(a, b)
        field.append(w)
        bracket.append(("R32", a, b, modal, w, pa, pb))
    for name in ("R16", "QF", "SF", "Final"):
        nxt = []
        for i in range(0, len(field), 2):
            a, b = field[i], field[i + 1]
            w, modal, pa, pb = advance(a, b)
            nxt.append(w)
            bracket.append((name, a, b, modal, w, pa, pb))
        field = nxt
    return {"winners": winners, "runners": runners, "best_thirds": sorted(best_groups),
            "third_by_group": third_by_group, "bracket": bracket, "champion": field[0],
            "expected_points": epts_all}


def _play_traced(model, a: str, b: str, rng) -> tuple[int, int, str, bool]:
    """One knockout tie -> (home_goals, away_goals, winner, went_to_shootout)."""
    gh, ga = model.sample_scoreline(a, b, neutral=True, rng=rng)
    if gh == ga:
        scale = getattr(model, "strength_scale", 400.0)
        delta = model.team_strength(a) - model.team_strength(b)
        winner = a if rng.random() < 1.0 / (1.0 + 10 ** (-delta / scale)) else b
        return gh, ga, winner, True
    return gh, ga, (a if gh > ga else b), False


def simulate_traced(model, group_teams: dict, seed: int) -> dict:
    """One fully-recorded tournament **realization** (not an average).

    Records every group fixture's scoreline + final standings, the 8 best third-placed teams,
    and the R32->Final bracket (each tie's scoreline, winner, and whether it went to a shootout)
    down to the champion. Same group/knockout structure as the shipped simulator.
    """
    rng = np.random.default_rng(seed)
    begin = getattr(model, "begin_tournament", None)
    if begin is not None:
        begin(rng)
    groups_out, winners, runners, thirds = {}, {}, {}, []
    for g, ts in group_teams.items():
        stats = {t: {"team": t, "pts": 0, "gf": 0, "ga": 0} for t in ts}
        fixtures = []
        for a, b in combinations(ts, 2):
            ga_, gb_ = model.sample_scoreline(a, b, neutral=True, rng=rng)
            stats[a]["gf"] += ga_; stats[a]["ga"] += gb_
            stats[b]["gf"] += gb_; stats[b]["ga"] += ga_
            if ga_ > gb_:
                stats[a]["pts"] += 3
            elif gb_ > ga_:
                stats[b]["pts"] += 3
            else:
                stats[a]["pts"] += 1; stats[b]["pts"] += 1
            fixtures.append((a, b, int(ga_), int(gb_)))
        table = list(stats.values())
        for s in table:
            s["gd"] = s["gf"] - s["ga"]
        rng.shuffle(table)
        table.sort(key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)
        groups_out[g] = {"table": table, "fixtures": fixtures}
        winners[g] = table[0]["team"]; runners[g] = table[1]["team"]
        thirds.append({**table[2], "group": g})
    best = sorted(thirds, key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)[:8]
    third_by_group = {s["group"]: s["team"] for s in best}

    field, bracket = [], []
    for a, b in r32_matchups(winners, runners, third_by_group):
        gh, ga, w, pens = _play_traced(model, a, b, rng)
        field.append(w)
        bracket.append(("R32", a, b, gh, ga, w, pens))
    for name in ("R16", "QF", "SF", "Final"):
        nxt = []
        for i in range(0, len(field), 2):
            a, b = field[i], field[i + 1]
            gh, ga, w, pens = _play_traced(model, a, b, rng)
            nxt.append(w)
            bracket.append((name, a, b, gh, ga, w, pens))
        field = nxt
    return {"groups": groups_out, "best_thirds": [s["group"] for s in best],
            "third_by_group": third_by_group, "bracket": bracket, "champion": field[0]}
