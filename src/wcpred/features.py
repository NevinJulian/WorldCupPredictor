"""Feature engineering -> the modelling table (one row per match).

Every feature is **as-of kickoff**: a team's pre-match Elo, and rolling form computed only
from *prior* matches (shift(1) before any rolling window). No future information leaks in.

Main entry point:
    build_features(matches_with_elo, ranking=None, hosts=None) -> wide DataFrame
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import DATA_RAW
from .confederations import confederation

FORM_WINDOWS = (5, 10)
EWM_HALFLIFE = 5

# Hosts of WC 2026 (used only when building the 2026 fixture features).
HOSTS_2026 = {"Canada", "Mexico", "United States"}

# Ranking-file team names -> results-file team names (best-effort reconciliation).
_RANK_ALIASES = {
    "USA": "United States", "Korea Republic": "South Korea", "Korea DPR": "North Korea",
    "IR Iran": "Iran", "China PR": "China", "Côte d'Ivoire": "Ivory Coast",
    "Czech Republic": "Czechia", "Cabo Verde": "Cape Verde", "Türkiye": "Turkey",
    "Curaçao": "Curacao", "Congo DR": "DR Congo", "Kyrgyz Republic": "Kyrgyzstan",
}


# --------------------------------------------------------------------------- #
# FIFA ranking
# --------------------------------------------------------------------------- #
def load_fifa_ranking(raw_dir: Path | None = None) -> pd.DataFrame | None:
    """Load and normalise the FIFA ranking file to [team, date, rank, rank_points].

    Tolerant of the two common mirror schemas (cnc8 / Dato-Futbol). Returns None if absent.
    """
    raw_dir = raw_dir or DATA_RAW
    fp = raw_dir / "fifa_ranking.csv"
    if not fp.exists():
        return None
    df = pd.read_csv(fp)
    cols = {c.lower(): c for c in df.columns}

    def pick(*cands):
        for c in cands:
            if c in cols:
                return cols[c]
        return None

    team_c = pick("country_full", "team", "country", "nation", "name")
    date_c = pick("rank_date", "date", "ranking_date")
    rank_c = pick("rank", "position", "ranking")
    pts_c = pick("total_points", "points", "rank_points", "points_total")
    # Need team + date, and either an explicit rank OR points to derive one from.
    if not (team_c and date_c) or not (rank_c or pts_c):
        print("  ranking: unrecognised schema; skipping rank features.")
        return None

    out = df.rename(columns={team_c: "team", date_c: "date"})
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["rank_points"] = pd.to_numeric(df[pts_c], errors="coerce") if pts_c else np.nan
    if rank_c:
        out["rank"] = pd.to_numeric(df[rank_c], errors="coerce")
    else:
        # Mirrors like Dato-Futbol have no rank column — teams are just ordered by points
        # each date. Derive rank = position by descending points within each date.
        out["rank"] = out.groupby("date")["rank_points"].rank(ascending=False, method="min")
    out["team"] = out["team"].astype(str).replace(_RANK_ALIASES)
    out = out.dropna(subset=["team", "date", "rank"])
    return out[["team", "date", "rank", "rank_points"]].sort_values("date")


def merge_ranking_asof(matches: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    """Attach each team's most recent FIFA rank as of the match date (backward asof)."""
    m = matches.copy()
    rank_sorted = ranking.sort_values("date")

    def side(team_col: str, prefix: str) -> pd.DataFrame:
        left = (
            m[["match_id", "date", team_col]]
            .rename(columns={team_col: "team"})
            .sort_values("date")
        )
        merged = pd.merge_asof(left, rank_sorted, on="date", by="team", direction="backward")
        return merged.set_index("match_id")[["rank", "rank_points"]].add_prefix(prefix)

    home = side("home_team", "home_")
    away = side("away_team", "away_")
    m = m.set_index("match_id").join(home).join(away).reset_index()
    m["rank_diff"] = m["home_rank"] - m["away_rank"]          # negative => home better
    m["rank_points_diff"] = m["home_rank_points"] - m["away_rank_points"]
    return m


# --------------------------------------------------------------------------- #
# Long (team-perspective) view + rolling form
# --------------------------------------------------------------------------- #
def _long_view(matches: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    m = matches.reset_index(drop=True).copy()
    m["match_id"] = m.index

    def perspective(is_home: bool) -> pd.DataFrame:
        gf = m["home_score"] if is_home else m["away_score"]
        ga = m["away_score"] if is_home else m["home_score"]
        return pd.DataFrame({
            "match_id": m["match_id"], "date": m["date"], "is_home": int(is_home),
            "team": m["home_team"] if is_home else m["away_team"],
            "team_elo": m["elo_home"] if is_home else m["elo_away"],
            "opp_elo": m["elo_away"] if is_home else m["elo_home"],
            "gf": gf, "ga": ga,
        })

    long = pd.concat([perspective(True), perspective(False)], ignore_index=True)
    long["points"] = np.select(
        [long["gf"] > long["ga"], long["gf"] == long["ga"]], [3.0, 1.0], default=0.0
    )
    long.loc[long["gf"].isna(), "points"] = np.nan
    long["gd"] = long["gf"] - long["ga"]
    return m, long.sort_values(["team", "date"], kind="stable").reset_index(drop=True)


def _rolling_team_features(long: pd.DataFrame) -> pd.DataFrame:
    """All features here use only matches strictly BEFORE the current row."""
    g = long.groupby("team", sort=False)

    # Rest & congestion.
    long["rest_days"] = (long["date"] - g["date"].shift(1)).dt.days

    # Recency- and window-based form (shift(1) => exclude current match).
    for w in FORM_WINDOWS:
        long[f"form_ppg_{w}"] = g["points"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        long[f"form_gf_{w}"] = g["gf"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        long[f"form_ga_{w}"] = g["ga"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        long[f"form_gd_{w}"] = g["gd"].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
    long["form_ewm_ppg"] = g["points"].transform(
        lambda s: s.shift(1).ewm(halflife=EWM_HALFLIFE, min_periods=1).mean()
    )
    # Over/under-performance vs Elo expectation, recent (are they on a hot streak?).
    long["elo_exp_pts"] = 3.0 / (1.0 + 10.0 ** (-(long["team_elo"] - long["opp_elo"]) / 400.0))
    long["_perf"] = long["points"] - long["elo_exp_pts"]
    long["form_vs_elo_5"] = g["_perf"].transform(
        lambda s: s.shift(1).rolling(5, min_periods=1).mean()
    )

    # Matches in the previous 30 days (fatigue), counting only PRIOR matches. Dates are
    # already ascending within each team, so a searchsorted gives the count directly —
    # vectorised, and avoids the groupby.apply grouping-columns deprecation.
    def _count_30d(dates: pd.Series) -> pd.Series:
        d = dates.to_numpy()
        lo = np.searchsorted(d, d - np.timedelta64(30, "D"), side="left")
        return pd.Series(np.arange(len(d)) - lo, index=dates.index, dtype=float)

    long["matches_30d"] = long.groupby("team")["date"].transform(_count_30d)
    return long.drop(columns=["_perf", "elo_exp_pts"])


def _pivot_back(matches: pd.DataFrame, long: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    home = long[long["is_home"] == 1].set_index("match_id")[feature_cols].add_prefix("home_")
    away = long[long["is_home"] == 0].set_index("match_id")[feature_cols].add_prefix("away_")
    out = matches.set_index("match_id").join(home).join(away).reset_index()
    # Symmetric difference features (home minus away).
    for c in feature_cols:
        out[f"{c}_diff"] = out[f"home_{c}"] - out[f"away_{c}"]
    return out


# --------------------------------------------------------------------------- #
# Public builder
# --------------------------------------------------------------------------- #
def build_features(
    matches_with_elo: pd.DataFrame,
    ranking: pd.DataFrame | None = None,
    hosts: set[str] | None = None,
) -> pd.DataFrame:
    """Assemble the wide, one-row-per-match modelling table from Elo-augmented matches."""
    matches, long = _long_view(matches_with_elo)
    long = _rolling_team_features(long)

    feature_cols = (
        ["rest_days", "form_ewm_ppg", "form_vs_elo_5", "matches_30d"]
        + [f"form_{m}_{w}" for w in FORM_WINDOWS for m in ("ppg", "gf", "ga", "gd")]
    )
    wide = _pivot_back(matches, long, feature_cols)

    # FIFA ranking (optional).
    if ranking is not None and len(ranking):
        wide = merge_ranking_asof(wide, ranking)

    # Confederation + host context.
    wide["home_confed"] = wide["home_team"].map(confederation)
    wide["away_confed"] = wide["away_team"].map(confederation)
    wide["same_confed"] = (wide["home_confed"] == wide["away_confed"]).astype(int)
    hosts = hosts or set()
    wide["home_is_host"] = wide["home_team"].isin(hosts).astype(int)
    wide["away_is_host"] = wide["away_team"].isin(hosts).astype(int)

    return wide


def feature_columns(df: pd.DataFrame) -> list[str]:
    """The model-input columns (excludes identifiers, raw scores, and targets)."""
    drop = {
        "match_id", "date", "home_team", "away_team", "home_score", "away_score",
        "tournament", "city", "country", "neutral", "played", "result", "margin",
        "total_goals", "year", "home_confed", "away_confed",
        "elo_home_post", "elo_away_post", "elo_k",
    }
    return [c for c in df.columns if c not in drop and df[c].dtype != object]
