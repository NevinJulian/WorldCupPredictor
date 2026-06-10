"""WC 2026 Monte-Carlo simulator (skeleton).

It runs out-of-the-box on an Elo-based match model so you can see end-to-end output today;
swap in your trained goals model later by passing any object with
`sample_scoreline(home, away, neutral, rng) -> (home_goals, away_goals)`.

Format encoded: 12 groups of 4 -> top 2 + 8 best third-placed -> R32 -> ... -> Final.

NOTE on the bracket: group-stage and "advance" probabilities are correct. The exact R32
slotting of the 8 third-placed teams follows FIFA's Annex-C table (495 combinations) and is
approximated here by seeding the 32 qualifiers (by ``model.team_strength``) into a standard
bracket. Finalise this mapping before trusting deep-run / title odds. See PLAN.md §6.
"""
from __future__ import annotations

from dataclasses import dataclass
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


def _standard_seed_order(size: int) -> list[int]:
    """1-indexed seed sitting at each bracket slot, so #1 meets #size, #2 meets #size-1, etc."""
    seeds = [1]
    while len(seeds) < size:
        n = len(seeds) * 2
        nxt = []
        for s in seeds:
            nxt.append(s)
            nxt.append(n + 1 - s)
        seeds = nxt
    return seeds


def _knockout(qualifiers: list[str], model, rng) -> dict[str, int]:
    """Strength-seeded single elimination, robust to non-power-of-2 fields (top seeds get byes).

    Seeding and the shootout tiebreak both read ``model.team_strength`` (the match-model
    interface), so the simulator no longer needs a separate Elo ratings dict. Returns
    team -> furthest round SIZE reached: 32 = lost in the round of 32, 16 = reached the
    round of 16, ... , 2 = reached the final, 1 = champion.
    """
    seeded = sorted(qualifiers, key=model.team_strength, reverse=True)
    n = len(seeded)
    if n <= 1:
        return {t: 1 for t in seeded}
    size = 1 << (n - 1).bit_length()  # next power of two >= n
    positions = _standard_seed_order(size)
    field = [seeded[p - 1] if p - 1 < n else None for p in positions]  # None = bye
    reached = {t: size for t in seeded}

    def alive(f):
        return [x for x in f if x is not None]

    while len(alive(field)) > 1:
        nxt = []
        for i in range(0, len(field), 2):
            a, b = field[i], field[i + 1]
            if a is None or b is None:
                nxt.append(a if b is None else b)  # bye (or None vs None -> None)
                continue
            ga, gb = model.sample_scoreline(a, b, neutral=True, rng=rng)
            if ga == gb:  # extra time + shootout ~ strength-weighted coin flip
                scale = getattr(model, "strength_scale", 400.0)
                delta = model.team_strength(a) - model.team_strength(b)
                pa = 1.0 / (1.0 + 10 ** (-delta / scale))
                winner = a if rng.random() < pa else b
            else:
                winner = a if ga > gb else b
            nxt.append(winner)
        field = nxt
        n_alive = len(alive(field))
        for w in alive(field):
            reached[w] = n_alive  # advanced into a round containing `n_alive` teams
    return reached


def simulate_tournament(
    groups: pd.DataFrame, model, n_sims: int = 10000, seed: int = 0
) -> pd.DataFrame:
    """Run the Monte-Carlo and return per-team advancement/title probabilities.

    `model` is any object implementing the match-model interface: ``sample_scoreline`` for
    goals and ``team_strength`` (+ optional ``strength_scale``) for knockout seeding and the
    shootout tiebreak.
    """
    rng = np.random.default_rng(seed)
    group_names = sorted(groups["group"].unique())
    group_teams = {g: groups.loc[groups["group"] == g, "team"].tolist() for g in group_names}
    teams = groups["team"].tolist()

    counts = {t: {k: 0 for k in ["win_group", "runner_up", "advance",
                                 "R16", "QF", "SF", "Final", "Winner"]} for t in teams}

    for _ in range(n_sims):
        winners, runners, thirds = [], [], []
        for g in group_names:
            table = _simulate_group(group_teams[g], model, rng)
            counts[table[0]["team"]]["win_group"] += 1
            counts[table[1]["team"]]["runner_up"] += 1
            winners.append(table[0]["team"])
            runners.append(table[1]["team"])
            thirds.append(table[2])
        best_thirds = [s["team"] for s in sorted(
            thirds, key=lambda s: (s["pts"], s["gd"], s["gf"]), reverse=True)[:8]]

        qualifiers = winners + runners + best_thirds
        for t in qualifiers:
            counts[t]["advance"] += 1

        reached = _knockout(qualifiers, model, rng)  # team -> round size reached
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
