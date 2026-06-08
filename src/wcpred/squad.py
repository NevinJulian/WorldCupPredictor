"""ADVANCED features: squad market value + current injuries (Transfermarkt).

Honest scope:
  * Market value & injuries are a **current snapshot**, not a historical time series. Use them
    for the **2026 prediction layer** and the "does squad strength add signal?" experiment on
    the modern subset — NOT for the 1872+ backtest (you cannot reconstruct a 1998 injury list).
  * Transfermarkt's HTML changes periodically. The CSS selectors below are best-effort; if a
    parse returns nothing, update the selectors or drop a manually-collected CSV into
    data/raw/squad/manual_squad_values.csv with columns [team, squad_value_eur_m, n_injured,
    injured_value_share, avg_age].

Etiquette: low request rate, descriptive User-Agent, personal/research use only.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover
    requests = None
    BeautifulSoup = None

USER_AGENT = "WorldCupPredictor/0.1 (research; contact: you@example.com)"
REQUEST_DELAY_S = 4.0  # be polite

# National team -> Transfermarkt slug + id. Extend as needed (find the id in the team URL).
# Example URL: https://www.transfermarkt.com/brasilien/startseite/verein/3439
TM_TEAMS: dict[str, tuple[str, int]] = {
    "Brazil": ("brasilien", 3439),
    "Argentina": ("argentinien", 3437),
    "France": ("frankreich", 3377),
    "England": ("england", 3299),
    "Spain": ("spanien", 3375),
    "Germany": ("deutschland", 3262),
    "Portugal": ("portugal", 3300),
    "Netherlands": ("niederlande", 3379),
    "Belgium": ("belgien", 3382),
    # ... add the rest of the 48 finalists; the loader skips any team not listed.
}


def _money_to_millions(text: str) -> float | None:
    """'€1.20bn' / '€850.00m' / '€500k' -> millions of euros."""
    if not text:
        return None
    t = text.replace("\xa0", " ").strip().lower().replace("€", "")
    m = re.search(r"([\d.,]+)\s*(bn|m|k)?", t)
    if not m:
        return None
    val = float(m.group(1).replace(",", ""))
    unit = m.group(2)
    return {"bn": val * 1000, "m": val, "k": val / 1000, None: val}[unit]


def fetch_squad_page(slug: str, team_id: int, session) -> str | None:  # pragma: no cover - network
    url = f"https://www.transfermarkt.com/{slug}/kader/verein/{team_id}/plus/1"
    r = session.get(url, timeout=30)
    if r.status_code != 200:
        print(f"  {slug}: HTTP {r.status_code}")
        return None
    return r.text


def parse_squad(html: str) -> pd.DataFrame:  # pragma: no cover - parsing
    """Parse the squad table into [player, age, market_value_m, injured]."""
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for tr in soup.select("table.items > tbody > tr"):
        mv = tr.select_one("td.rechts.hauptlink")
        age_cell = tr.find_all("td", class_="zentriert")
        injured = bool(tr.select_one("span.verletzt-table, .icons_sprite.verletzt"))
        if mv is None:
            continue
        value_m = _money_to_millions(mv.get_text())
        age = None
        for c in age_cell:
            m = re.search(r"\((\d{2})\)", c.get_text())
            if m:
                age = int(m.group(1))
                break
        rows.append({"market_value_m": value_m, "age": age, "injured": injured})
    return pd.DataFrame(rows)


def squad_to_features(team: str, squad: pd.DataFrame) -> dict:
    """Aggregate a parsed squad into team-level features."""
    sq = squad.dropna(subset=["market_value_m"])
    total = sq["market_value_m"].sum()
    inj_val = sq.loc[sq["injured"], "market_value_m"].sum()
    return {
        "team": team,
        "squad_value_eur_m": round(total, 1),
        "top11_value_eur_m": round(sq["market_value_m"].nlargest(11).sum(), 1),
        "avg_age": round(sq["age"].mean(), 1) if "age" in sq else None,
        "n_injured": int(sq["injured"].sum()),
        "injured_value_share": round(inj_val / total, 3) if total else 0.0,
    }


def scrape_all(out_dir: Path, teams: dict | None = None) -> pd.DataFrame:  # pragma: no cover
    """Scrape every configured team, cache to data/raw/squad/squad_features.csv."""
    if requests is None or BeautifulSoup is None:
        raise ImportError("Install requests + beautifulsoup4 + lxml for the advanced tier.")
    teams = teams or TM_TEAMS
    sub = Path(out_dir) / "squad"
    sub.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    feats = []
    for team, (slug, tid) in teams.items():
        print(f"  squad: {team}")
        html = fetch_squad_page(slug, tid, session)
        if html:
            feats.append(squad_to_features(team, parse_squad(html)))
        time.sleep(REQUEST_DELAY_S)

    df = pd.DataFrame(feats)
    if df.empty:
        print("  No squads parsed — check selectors or supply manual_squad_values.csv")
    else:
        df.to_csv(sub / "squad_features.csv", index=False)
        print(f"  saved squad_features.csv ({len(df)} teams)")
    return df


def load_squad_features(raw_dir: Path) -> pd.DataFrame | None:
    """Read cached squad features (scraped or manual). Returns None if absent."""
    for name in ("squad/squad_features.csv", "squad/manual_squad_values.csv"):
        fp = Path(raw_dir) / name
        if fp.exists():
            return pd.read_csv(fp)
    return None
