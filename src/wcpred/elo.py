"""World Football Elo, computed in-house from the match table.

Why compute it ourselves instead of downloading Elo?
  * No external dependency, and it always covers the latest matches.
  * It is **as-of by construction** — the rating attached to a match is the rating BEFORE
    that match, so there is zero look-ahead leakage.
  * We control the K-factors and home-advantage constant and can tune them.

Rules follow eloratings.net (World Football Elo Ratings):
    R_new = R_old + K * G * (W - We)
where
    We   = 1 / (1 + 10 ** (-(dr) / 400)),   dr = elo_home - elo_away + home_adv
    W    = 1 / 0.5 / 0 for home win / draw / loss
    G    = goal-difference multiplier (1, 1.5, 1.75, then +1/8 per extra goal)
    K    = importance weight from the tournament label (friendly 20 ... World Cup 60)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

DEFAULT_RATING = 1500.0
DEFAULT_HOME_ADV = 100.0

# Tournament-importance K weights (eloratings.net tiers).
K_FRIENDLY = 20
K_MINOR = 30
K_QUALIFIER = 40
K_CONTINENTAL = 50
K_WORLD_CUP = 60

# Regex patterns matched (case-insensitive) against the `tournament` column, in order.
_K_PATTERNS: list[tuple[str, int]] = [
    (r"friendly", K_FRIENDLY),
    (r"qualif", K_QUALIFIER),                       # WC + continental qualifiers
    (r"fifa world cup\b(?!.*qualif)", K_WORLD_CUP),  # World Cup finals
    (r"(uefa euro|copa am[eé]rica|african cup|afc asian cup|gold cup|"
     r"confederations cup|oceania nations)", K_CONTINENTAL),
    (r"(nations league|king's cup|kirin|gulf cup|cosafa|"
     r"championship|cup|trophy|games)", K_MINOR),
]


def k_for_tournament(tournament: str) -> int:
    """Map a tournament label to its Elo K-factor."""
    t = (tournament or "").lower()
    # World Cup finals must win over the generic 'cup' rule, so check it explicitly first.
    if "fifa world cup" in t and "qualif" not in t:
        return K_WORLD_CUP
    for pat, k in _K_PATTERNS:
        if re.search(pat, t):
            return k
    return K_MINOR  # unknown competitive match


def goal_diff_multiplier(margin: int) -> float:
    """eloratings goal-difference weighting."""
    m = abs(int(margin))
    if m <= 1:
        return 1.0
    if m == 2:
        return 1.5
    if m == 3:
        return 1.75
    return 1.75 + (m - 3) / 8.0


def expected_score(elo_home: float, elo_away: float, home_adv: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (-(elo_home - elo_away + home_adv) / 400.0))


@dataclass
class EloModel:
    home_adv: float = DEFAULT_HOME_ADV
    default_rating: float = DEFAULT_RATING
    ratings: dict[str, float] = field(default_factory=dict)
    last_played: dict[str, "pd.Timestamp"] = field(default_factory=dict)

    def rating(self, team: str) -> float:
        return self.ratings.get(team, self.default_rating)

    def run(self, results: pd.DataFrame) -> pd.DataFrame:
        """Process matches chronologically; return a copy with pre-match Elo columns.

        Adds: elo_home, elo_away (pre-match), elo_diff, elo_expected_home,
        elo_home_post, elo_away_post, elo_k.
        Also records `last_played` so callers can compute rest days / current ratings.
        """
        df = results.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", kind="stable").reset_index(drop=True)

        n = len(df)
        elo_h = np.empty(n)
        elo_a = np.empty(n)
        exp_h = np.empty(n)
        elo_h_post = np.empty(n)
        elo_a_post = np.empty(n)
        k_arr = np.empty(n)

        for i, row in enumerate(df.itertuples(index=False)):
            home, away = row.home_team, row.away_team
            hs, as_ = row.home_score, row.away_score
            neutral = bool(getattr(row, "neutral", False))

            rh, ra = self.rating(home), self.rating(away)
            adv = 0.0 if neutral else self.home_adv
            we = expected_score(rh, ra, adv)

            elo_h[i], elo_a[i], exp_h[i] = rh, ra, we

            # Skip the update if the score is missing (future / unplayed fixtures).
            if pd.isna(hs) or pd.isna(as_):
                elo_h_post[i], elo_a_post[i], k_arr[i] = rh, ra, np.nan
                continue

            w = 1.0 if hs > as_ else (0.5 if hs == as_ else 0.0)
            k = k_for_tournament(row.tournament)
            g = goal_diff_multiplier(hs - as_)
            delta = k * g * (w - we)

            self.ratings[home] = rh + delta
            self.ratings[away] = ra - delta
            self.last_played[home] = row.date
            self.last_played[away] = row.date
            elo_h_post[i], elo_a_post[i], k_arr[i] = rh + delta, ra - delta, k

        df["elo_home"] = elo_h
        df["elo_away"] = elo_a
        df["elo_diff"] = elo_h - elo_a
        df["elo_expected_home"] = exp_h
        df["elo_home_post"] = elo_h_post
        df["elo_away_post"] = elo_a_post
        df["elo_k"] = k_arr
        return df


def compute_elo(results: pd.DataFrame, home_adv: float = DEFAULT_HOME_ADV) -> tuple[pd.DataFrame, EloModel]:
    """Convenience wrapper. Returns (matches_with_elo, fitted_model)."""
    model = EloModel(home_adv=home_adv)
    return model.run(results), model


def current_ratings_table(model: EloModel) -> pd.DataFrame:
    """Snapshot of every team's latest Elo (for the 2026 prediction layer)."""
    return (
        pd.DataFrame(
            {"team": list(model.ratings), "elo": list(model.ratings.values())}
        )
        .assign(last_played=lambda d: d["team"].map(model.last_played))
        .sort_values("elo", ascending=False)
        .reset_index(drop=True)
    )
