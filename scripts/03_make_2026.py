"""Generate WC 2026 group fixtures and a baseline Monte-Carlo forecast.

    python scripts/03_make_2026.py [--sims 20000]

Output (data/processed/):
    wc2026_group_fixtures.csv  — all 72 group-stage matches
    wc2026_odds.csv            — per-team advance / round / title probabilities (Elo baseline)

The forecast here uses the Elo stand-in match model. Once you've trained the real ensembled
goals+outcome model, swap it into tournament.simulate_tournament (see PLAN.md §5-6).
"""
import pathlib
import sys
from itertools import combinations

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, clean, elo, tournament  # noqa: E402

# groups_2026 name -> martj42 results name, for any that differ.
NAME_ALIASES = {
    "Türkiye": "Turkey", "Czechia": "Czech Republic", "Curaçao": "Curacao",
    "South Korea": "Korea Republic", "Cape Verde": "Cabo Verde",
}


def resolve(team: str, ratings: dict) -> str:
    if team in ratings:
        return team
    for cand in (NAME_ALIASES.get(team), team.replace("ü", "u")):
        if cand and cand in ratings:
            return cand
    return team  # unresolved -> will use median rating + a warning


def main(sims: int = 20000) -> int:
    print("Computing current Elo from match history...")
    matches = clean.load_clean_results()
    _, model = elo.compute_elo(matches)
    ratings = model.ratings

    groups = tournament.load_groups()
    groups["team_resolved"] = groups["team"].map(lambda t: resolve(t, ratings))
    missing = sorted(set(groups.loc[~groups["team_resolved"].isin(ratings), "team"]))
    if missing:
        print(f"  WARNING: no Elo for {missing} (name mismatch?) — using median rating.")

    # Group fixtures (round-robin within each group).
    fixtures = [
        {"group": g, "home": a, "away": b}
        for g, sub in groups.groupby("group")
        for a, b in combinations(sub["team"].tolist(), 2)
    ]
    fx = pd.DataFrame(fixtures)
    fx.to_csv(DATA_PROCESSED / "wc2026_group_fixtures.csv", index=False)
    print(f"  {len(fx)} group fixtures -> wc2026_group_fixtures.csv")

    # Simulate using resolved names so Elo lookups hit.
    sim_groups = groups.assign(team=groups["team_resolved"])
    mm = tournament.EloMatchModel(ratings)
    print(f"Simulating {sims:,} tournaments (Elo baseline)...")
    odds = tournament.simulate_tournament(sim_groups, mm, ratings, n_sims=sims)
    # restore display names
    back = dict(zip(groups["team_resolved"], groups["team"]))
    odds["team"] = odds["team"].map(lambda t: back.get(t, t))
    odds.to_csv(DATA_PROCESSED / "wc2026_odds.csv", index=False)

    print("\nTop 15 title contenders (Elo baseline — NOT the final model):")
    show = odds.head(15)[["team", "advance", "SF", "Final", "Winner"]]
    print(show.to_string(index=False))
    print(f"\nFull table -> {DATA_PROCESSED / 'wc2026_odds.csv'}")
    return 0


if __name__ == "__main__":
    n = 20000
    if "--sims" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sims") + 1])
    raise SystemExit(main(n))
