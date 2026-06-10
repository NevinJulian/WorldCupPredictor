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

import numpy as np
import pandas as pd

from . import clean, datasets, elo, features
from .models import EnsembleModel
from .tournament import load_groups

# Elo points -> natural log-odds (the standard Elo logistic), for the strength-shock tilt.
_ELO_LOGIT = math.log(10.0) / 400.0

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
):
    """Fit the ensemble on all played data and assemble the 2026 `ForecastMatchModel`.

    ``rating_sigma`` (Elo) turns on the per-tournament strength-shock dispersion lever; it is
    0 (off) by default because the backtest does not support it (reports/sim_dispersion_2026.md).

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

    ens = EnsembleModel(**(ensemble_kwargs or {})).fit(datasets.played_only(feat))
    dc = ens.dc_

    g = groups.copy()
    g["team_data"] = g["team"].map(lambda t: resolve_team(t, ratings))
    teams = g["team_data"].tolist()
    unresolved = sorted(set(g.loc[~g["team_data"].isin(ratings), "team"]))

    # Per-team current snapshot from played history only (leakage-free, no contamination).
    snap = team_snapshot(matches[matches["played"]].copy(), ranking, teams, features.HOSTS_2026)

    # Knockout layer: every ordered pair on neutral ground, scored by the ensemble.
    pairs = [(a, b) for a in teams for b in teams if a != b]
    pair_probs = ens.predict_proba(assemble_pairs(snap, pairs))
    matrices: dict[tuple[str, str], np.ndarray] = {}
    for (a, b), pr in zip(pairs, pair_probs):
        matrices[(a, b)] = reweight_to_outcome(dc.score_matrix(a, b, neutral=True), pr)

    # Group layer: the real fixtures override their neutral entries with the true venue
    # (host advantage). Both orderings are stored so the round-robin hits them either way.
    grp = feat[(feat["tournament"] == "FIFA World Cup") & (~feat["played"])
               & feat["home_team"].isin(teams) & feat["away_team"].isin(teams)].copy()
    n_group = 0
    if len(grp):
        for (_, r), pr in zip(grp.iterrows(), ens.predict_proba(grp)):
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
            "n_group_fixtures": n_group, "unresolved": unresolved}
    return model, sim_groups, display_to_data, info
