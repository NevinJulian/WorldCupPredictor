"""WC 2026 Monte-Carlo simulator (skeleton).

It runs out-of-the-box on an Elo-based match model so you can see end-to-end output today;
swap in your trained goals model later by passing any object with
`sample_scoreline(home, away, neutral, rng) -> (home_goals, away_goals)`.

Format encoded: 12 groups of 4 -> top 2 + 8 best third-placed -> R32 -> ... -> Final.

The R32 slotting of the 8 best third-placed teams follows FIFA's real **Annex C** table
(495 combinations; see ``config/annexc_r32.csv`` / ``scripts/gen_annexc_table.py``) and the
bracket is wired to the published match tree, so deep-run / title odds are now exact for this
format (no more strength-seeded approximation). The simulator is therefore specific to the
2026 format: it requires the 12 groups A-L.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from . import CONFIG_DIR


# --------------------------------------------------------------------------- #
# Match models
# --------------------------------------------------------------------------- #
@dataclass
class EloMatchModel:
    """Elo -> bivariate-Poisson goals. A stand-in until the real model is trained."""
    ratings: dict[str, float]
    base_goals: float = 1.35     # avg goals per team
    elo_scale: float = 0.0029    # supremacy sensitivity to Elo diff (~1.16/400)
    home_adv: float = 65.0       # Elo points; 0 effectively for neutral games
    strength_scale: float = 400.0  # Elo points; the eloratings logistic denominator

    def default_rating(self) -> float:
        return float(np.median(list(self.ratings.values()))) if self.ratings else 1500.0

    def team_strength(self, team: str) -> float:
        """The team's Elo rating — the match-model interface used for seeding/tiebreaks."""
        return float(self.ratings.get(team, self.default_rating()))

    def lambdas(self, home: str, away: str, neutral: bool = True) -> tuple[float, float]:
        rh = self.ratings.get(home, self.default_rating())
        ra = self.ratings.get(away, self.default_rating())
        adv = 0.0 if neutral else self.home_adv
        delta = (rh - ra + adv) * self.elo_scale
        return self.base_goals * np.exp(delta), self.base_goals * np.exp(-delta)

    def sample_scoreline(self, home, away, neutral=True, rng=None) -> tuple[int, int]:
        rng = rng or np.random.default_rng()
        lh, la = self.lambdas(home, away, neutral)
        return int(rng.poisson(lh)), int(rng.poisson(la))


# --------------------------------------------------------------------------- #
# Groups
# --------------------------------------------------------------------------- #
def load_groups(path: Path | None = None) -> pd.DataFrame:
    path = path or (CONFIG_DIR / "groups_2026.csv")
    return pd.read_csv(path)


def _simulate_group(teams: list[str], model, rng) -> list[dict]:
    """Round-robin; return standings ranked by points, GD, GF (+ random tiebreak)."""
    stats = {t: {"team": t, "pts": 0, "gf": 0, "ga": 0} for t in teams}
    for a, b in combinations(teams, 2):
        ga, gb = model.sample_scoreline(a, b, neutral=True, rng=rng)
        stats[a]["gf"] += ga; stats[a]["ga"] += gb
        stats[b]["gf"] += gb; stats[b]["ga"] += ga
        if ga > gb:
            stats[a]["pts"] += 3
        elif gb > ga:
            stats[b]["pts"] += 3
        else:
            stats[a]["pts"] += 1; stats[b]["pts"] += 1
    table = list(stats.values())
    for s in table:
        s["gd"] = s["gf"] - s["ga"]
    rng.shuffle(table)  # random tiebreak for equal records
    table.sort(key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)
    return table


# --------------------------------------------------------------------------- #
# Knockout bracket — FIFA's real Annex-C round-of-32 slotting (2026 format)
# --------------------------------------------------------------------------- #
# The 8 group winners that face a best-third in the R32 (Matches 79/85/81/74/82/77/87/80),
# in the Annex-C table's column order.
_THIRD_FACING_WINNERS: tuple[str, ...] = ("A", "B", "D", "E", "G", "I", "K", "L")

# The 16 round-of-32 ties in *bracket-leaf order*: adjacent pairs feed one R16 tie, those feed
# the QFs, and so on up a clean 32-team single-elimination tree (no byes). Each participant is
# a slot: ("W", g) winner of group g; ("R", g) runner-up of group g; ("T", g) the best-third
# assigned to *winner group g* by Annex C. Order + adjacency transcribed from the published
# bracket (R16 Matches 89-96 -> QF 97-100 -> SF 101-102 -> Final).
_R32_BRACKET: tuple[tuple[tuple[str, str], tuple[str, str]], ...] = (
    (("W", "E"), ("T", "E")),   # M74
    (("W", "I"), ("T", "I")),   # M77
    (("R", "A"), ("R", "B")),   # M73
    (("W", "F"), ("R", "C")),   # M75
    (("W", "C"), ("R", "F")),   # M76
    (("R", "E"), ("R", "I")),   # M78
    (("W", "A"), ("T", "A")),   # M79
    (("W", "L"), ("T", "L")),   # M80
    (("R", "K"), ("R", "L")),   # M83
    (("W", "H"), ("R", "J")),   # M84
    (("W", "D"), ("T", "D")),   # M81
    (("W", "G"), ("T", "G")),   # M82
    (("W", "J"), ("R", "H")),   # M86
    (("R", "D"), ("R", "G")),   # M88
    (("W", "B"), ("T", "B")),   # M85
    (("W", "K"), ("T", "K")),   # M87
)


@lru_cache(maxsize=1)
def load_annexc(path: "str | None" = None) -> dict[frozenset, dict[str, str]]:
    """Annex C as {set of the 8 qualifying third-groups -> {winner group -> third group}}.

    Each of the 495 C(12,8) combinations of which groups' thirds advance maps to the
    predetermined R32 opponent (a group letter) for each of the 8 third-facing winners.
    Built by ``scripts/gen_annexc_table.py`` from the FWC2026 regulations' Annex C.
    """
    fp = Path(path) if path else (CONFIG_DIR / "annexc_r32.csv")
    df = pd.read_csv(fp)
    table = {frozenset(r["thirds"]): {w: r[w] for w in _THIRD_FACING_WINNERS}
             for _, r in df.iterrows()}
    if len(table) != 495:
        raise ValueError(f"Annex-C table has {len(table)} combinations, expected 495 ({fp}).")
    return table


def _play(a: str, b: str, model, rng) -> str:
    """One knockout tie: sample a scoreline; a draw is broken by a strength-weighted shootout."""
    ga, gb = model.sample_scoreline(a, b, neutral=True, rng=rng)
    if ga == gb:  # extra time + shootout ~ strength-weighted coin flip
        scale = getattr(model, "strength_scale", 400.0)
        delta = model.team_strength(a) - model.team_strength(b)
        return a if rng.random() < 1.0 / (1.0 + 10 ** (-delta / scale)) else b
    return a if ga > gb else b


def r32_matchups(winners: dict, runners: dict, thirds: dict) -> list[tuple[str, str]]:
    """The 16 round-of-32 ties (bracket-leaf order) for one group-stage outcome.

    ``winners``/``runners`` are {group -> team}; ``thirds`` is {group -> team} for only the 8
    groups whose third qualified. Annex C fixes each third-facing winner's opponent from the
    set of those 8 groups. Exposed so the slotting can be asserted against the published format.
    """
    slot_for_winner = load_annexc()[frozenset(thirds)]   # winner group -> the third's group

    def resolve(slot: tuple[str, str]) -> str:
        kind, g = slot
        if kind == "W":
            return winners[g]
        if kind == "R":
            return runners[g]
        return thirds[slot_for_winner[g]]                 # kind == "T": the Annex-C third
    return [(resolve(x), resolve(y)) for x, y in _R32_BRACKET]


def _knockout(winners: dict, runners: dict, thirds: dict, model, rng) -> dict[str, int]:
    """Play the real 2026 bracket from the 32 qualifiers; return team -> furthest round size.

    R32 ties come from `r32_matchups` (Annex-C slotting); the bracket then folds up a clean
    32-team tree. Returns team -> round SIZE reached: 32 = out in R32, 16 = R16, 8 = QF,
    4 = SF, 2 = final, 1 = champion (the buckets `simulate_tournament` counts).
    """
    matches = r32_matchups(winners, runners, thirds)
    reached = {t: 32 for tie in matches for t in tie}
    field = [_play(a, b, model, rng) for a, b in matches]   # 16 R32 winners (reached R16)
    size = 16
    for w in field:
        reached[w] = size
    while len(field) > 1:
        size //= 2                                          # 8 -> 4 -> 2 -> 1
        field = [_play(field[i], field[i + 1], model, rng) for i in range(0, len(field), 2)]
        for w in field:
            reached[w] = size
    return reached


def simulate_tournament(
    groups: pd.DataFrame, model, n_sims: int = 10000, seed: int = 0
) -> pd.DataFrame:
    """Run the Monte-Carlo and return per-team advancement/title probabilities.

    `model` is any object implementing the match-model interface: ``sample_scoreline`` for
    goals and ``team_strength`` (+ optional ``strength_scale``) for the shootout tiebreak.
    Requires the 12 groups A-L (the simulator models the real 2026 format / Annex-C bracket).
    """
    rng = np.random.default_rng(seed)
    group_names = sorted(groups["group"].unique())
    if set(group_names) != set("ABCDEFGHIJKL"):
        raise ValueError(
            "simulate_tournament models the 48-team 2026 format and needs exactly the 12 "
            f"groups A-L; got {group_names}."
        )
    group_teams = {g: groups.loc[groups["group"] == g, "team"].tolist() for g in group_names}
    teams = groups["team"].tolist()

    counts = {t: {k: 0 for k in ["win_group", "runner_up", "advance",
                                 "R16", "QF", "SF", "Final", "Winner"]} for t in teams}

    for _ in range(n_sims):
        winners, runners, thirds = {}, {}, []
        for g in group_names:
            table = _simulate_group(group_teams[g], model, rng)
            counts[table[0]["team"]]["win_group"] += 1
            counts[table[1]["team"]]["runner_up"] += 1
            winners[g] = table[0]["team"]
            runners[g] = table[1]["team"]
            thirds.append({**table[2], "group": g})
        best = sorted(thirds, key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)[:8]
        third_by_group = {s["group"]: s["team"] for s in best}

        qualifiers = list(winners.values()) + list(runners.values()) + list(third_by_group.values())
        for t in qualifiers:
            counts[t]["advance"] += 1

        reached = _knockout(winners, runners, third_by_group, model, rng)
        for t, sz in reached.items():
            if sz <= 16:
                counts[t]["R16"] += 1
            if sz <= 8:
                counts[t]["QF"] += 1
            if sz <= 4:
                counts[t]["SF"] += 1
            if sz <= 2:
                counts[t]["Final"] += 1
            if sz <= 1:
                counts[t]["Winner"] += 1

    rows = []
    for t in teams:
        c = counts[t]
        rows.append({"team": t, **{k: round(v / n_sims, 4) for k, v in c.items()}})
    return (
        pd.DataFrame(rows)
        .sort_values("Winner", ascending=False)
        .reset_index(drop=True)
    )
