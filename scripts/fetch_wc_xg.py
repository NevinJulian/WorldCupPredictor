"""Build data/raw/wc_xg_2018_2022.csv — per-match team xG for the 2018 & 2022 World Cups.

    python scripts/fetch_wc_xg.py

Source: **StatsBomb open data** (https://github.com/statsbomb/open-data), free for research/
education with attribution. We fetch the World Cup match lists (competition 43, seasons 3=2018,
106=2022) and each match's events, sum ``shot.statsbomb_xg`` per team, and write one compact CSV
(date, year, home/away team, goals, xG). This is the only source of WC xG, and it is used solely
for the in-tournament xG-adjustment GATE (reports/xg_adjust_gate.md) — never for live odds.

Team names already match the project's data spelling exactly (verified), so no aliasing is needed.
Run once; the small aggregated CSV is committed (raw events are not). Network required.
"""
from __future__ import annotations

import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402
import requests  # noqa: E402

from wcpred import DATA_RAW  # noqa: E402

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
HEADERS = {"User-Agent": "WorldCupPredictor/0.1 (research; StatsBomb open data, attributed)"}
SEASONS = {3: 2018, 106: 2022}        # StatsBomb season_id -> World Cup year (competition_id 43)
TIMEOUT = 60


def _get_json(url: str):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def match_team_xg(match_id: int) -> dict[str, float]:
    """Sum StatsBomb shot xG per team for one match."""
    xg: dict[str, float] = defaultdict(float)
    for e in _get_json(f"{BASE}/events/{match_id}.json"):
        if e.get("type", {}).get("name") == "Shot":
            xg[e["team"]["name"]] += float(e.get("shot", {}).get("statsbomb_xg", 0.0) or 0.0)
    return dict(xg)


def main() -> int:
    rows = []
    for season, year in SEASONS.items():
        matches = _get_json(f"{BASE}/matches/43/{season}.json")
        print(f"WC {year}: {len(matches)} matches — summing shot xG per match...")
        for i, m in enumerate(sorted(matches, key=lambda m: (m["match_date"], m["match_id"])), 1):
            home = m["home_team"]["home_team_name"]
            away = m["away_team"]["away_team_name"]
            xg = match_team_xg(m["match_id"])
            rows.append({
                "date": m["match_date"], "year": year, "home_team": home, "away_team": away,
                "home_goals": int(m["home_score"]), "away_goals": int(m["away_score"]),
                "home_xg": round(xg.get(home, 0.0), 3), "away_xg": round(xg.get(away, 0.0), 3),
            })
            if i % 16 == 0:
                print(f"  {i}/{len(matches)}")
    df = pd.DataFrame(rows).sort_values(["date", "home_team"]).reset_index(drop=True)
    out = DATA_RAW / "wc_xg_2018_2022.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nWrote {out}: {len(df)} matches "
          f"(2018: {(df.year == 2018).sum()}, 2022: {(df.year == 2022).sum()})")
    print(f"  mean xG/team {df[['home_xg', 'away_xg']].to_numpy().mean():.2f}, "
          f"mean goals/team {df[['home_goals', 'away_goals']].to_numpy().mean():.2f}")
    print("Source: StatsBomb open data (CC-attributed; research/education use).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
