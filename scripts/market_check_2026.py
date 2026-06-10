"""Market sanity check: model 2026 title odds vs de-vigged bookmaker odds.

    python scripts/market_check_2026.py

Analysis only — no model changes. Compares the simulator's WC 2026 title probabilities (from
data/processed/wc2026_forecast_odds.csv) against a de-vigged betting-market consensus, writes a
committed table + read to reports/market_check_2026.md, and prints the same.

De-vig method (as specified): implied = 1 / decimal (= 100/(american+100)), then renormalise
each book's full 48-team field to sum to 1 to strip the overround. "Market" = the mean of the
two sportsbooks' de-vigged probabilities; Kalshi (a prediction market) is shown as a third
reference. Odds are a snapshot captured 2026-06-10 (pre-tournament).
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED  # noqa: E402

SNAPSHOT_DATE = "2026-06-10"

# American outright-winner odds, full 48-team fields. Sources captured 2026-06-10:
#   DraftKings via ESPN; BetMGM via Yahoo Sports. (33-1 etc. written as the American +N.)
DRAFTKINGS = {
    "Spain": 450, "France": 475, "England": 700, "Portugal": 850, "Argentina": 900, "Brazil": 950,
    "Germany": 1400, "Netherlands": 2000, "Norway": 3500, "Belgium": 4000, "Colombia": 4000,
    "Morocco": 5000, "United States": 6000, "Switzerland": 6500, "Uruguay": 6500, "Japan": 6500,
    "Mexico": 8000, "Ecuador": 8000, "Turkey": 9000, "Croatia": 9000, "Senegal": 9000,
    "Sweden": 12000, "Austria": 15000, "Canada": 20000, "Scotland": 20000, "Ivory Coast": 25000,
    "Czechia": 25000, "Paraguay": 30000, "Egypt": 30000, "Ghana": 30000, "Algeria": 35000,
    "South Korea": 40000, "Bosnia and Herzegovina": 50000, "Tunisia": 50000, "Australia": 60000,
    "Iran": 70000, "DR Congo": 100000, "Saudi Arabia": 100000, "South Africa": 100000,
    "Panama": 100000, "Cape Verde": 100000, "Qatar": 150000, "Uzbekistan": 150000,
    "New Zealand": 150000, "Iraq": 150000, "Jordan": 250000, "Curacao": 250000, "Haiti": 250000,
}
BETMGM = {
    "Spain": 450, "France": 500, "England": 700, "Brazil": 800, "Argentina": 900, "Portugal": 900,
    "Germany": 1400, "Netherlands": 2000, "Belgium": 3300, "Norway": 3300, "Colombia": 4000,
    "Morocco": 4000, "Japan": 5000, "United States": 5000, "Mexico": 6600, "Senegal": 6600,
    "Switzerland": 6600, "Turkey": 6600, "Uruguay": 6600, "Croatia": 8000, "Ecuador": 8000,
    "Sweden": 10000, "Austria": 15000, "Canada": 15000, "Ivory Coast": 20000, "Algeria": 25000,
    "Bosnia and Herzegovina": 25000, "Czechia": 25000, "Egypt": 25000, "South Korea": 25000,
    "Paraguay": 25000, "Scotland": 25000, "Australia": 50000, "Ghana": 50000, "Iran": 50000,
    "Tunisia": 50000, "DR Congo": 75000, "Cape Verde": 100000, "Iraq": 100000, "Jordan": 100000,
    "New Zealand": 100000, "Panama": 100000, "Qatar": 100000, "Saudi Arabia": 100000,
    "South Africa": 100000, "Uzbekistan": 100000, "Curacao": 250000, "Haiti": 250000,
}
# Kalshi prediction-market implied probabilities (%), top names only (via covers.com).
KALSHI = {
    "Spain": 17.2, "France": 16.2, "England": 10.8, "Portugal": 10.7, "Argentina": 8.7,
    "Brazil": 8.4, "Germany": 5.6, "Netherlands": 4.7, "Norway": 2.5, "Belgium": 2.3,
    "Colombia": 2.0, "Mexico": 1.8, "Japan": 1.7, "Morocco": 1.7, "United States": 1.7,
    "Turkey": 1.2, "Switzerland": 1.0,
}

# 3-line diagnostic read (the interpretation — see the table it summarises).
READ = """\
1. The divergence is **not** uniform favourite-inflation (under-dispersion): the model over-rates
   Spain (x1.6) and the CONMEBOL sides Argentina (x2.6), Colombia (x2.5) and Ecuador (x2.7), while
   *under*-rating the European chasing pack — France, England, Portugal, Germany (x0.4-0.7). So the
   dominant signal is a team/confederation-specific tilt, not a global one.
2. Likely root cause (to investigate, not chase): the in-house Elo + form features over-value
   CONMEBOL teams — long intra-confederation qualifying and Argentina's unbeaten-run rating inflate
   them — and the Elo-heavy ensemble (w_gbm 0.89) compounds it over 7 rounds, concentrating 47% of
   the title in its top two vs the market's 24%. A single unseen injury can't explain a whole-region
   pattern, so this reads as systematic bias, not missing info.
3. There is *also* a mild global under-dispersion (model top-15 mass 0.94 vs market 0.86). Two
   no-code follow-ups worth doing: (a) audit ensemble H/D/A reliability on the backtest, and
   (b) check Elo strength by confederation vs the market. No model change is made here."""


def devig(book: dict) -> tuple[dict, float]:
    """Implied = 100/(american+100); renormalise the full field to sum 1 (strip the vig)."""
    implied = {t: 100.0 / (a + 100.0) for t, a in book.items()}
    overround = sum(implied.values())
    return {t: p / overround for t, p in implied.items()}, overround


def main() -> int:
    fp = DATA_PROCESSED / "wc2026_forecast_odds.csv"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/08_forecast_2026.py first.")
    model = pd.read_csv(fp).set_index("team")["title"]

    dk, or_dk = devig(DRAFTKINGS)
    mgm, or_mgm = devig(BETMGM)
    market = {t: (dk[t] + mgm[t]) / 2 for t in dk if t in mgm}

    top = model.sort_values(ascending=False).head(15)
    rows = []
    for team, m in top.items():
        mk = market.get(team)
        kal = KALSHI.get(team)
        rows.append({
            "team": team, "model": m, "market": mk,
            "gap_pp": (m - mk) * 100 if mk else None,
            "ratio": m / mk if mk else None,
            "kalshi": kal / 100 if kal else None,
        })
    tbl = pd.DataFrame(rows)

    top2_model = float(top.iloc[0] + top.iloc[1])
    top2_market = market[top.index[0]] + market[top.index[1]]
    mass_model = float(top.sum())
    mass_market = sum(market[t] for t in top.index)

    # ---- write the committed report ----
    def pct(x):
        return f"{x*100:.1f}%" if x is not None and pd.notna(x) else "—"

    lines = [
        "# WC 2026 — model title odds vs the betting market",
        "",
        f"*Analysis only (no model change). Odds snapshot: **{SNAPSHOT_DATE}**, pre-tournament.*",
        "",
        "**Method.** De-vig each book: implied = 1/decimal = 100/(american+100), then renormalise "
        "the full 48-team field to sum to 1. **Market** = mean of the two sportsbooks' de-vigged "
        "probabilities. Sources: **DraftKings** (via ESPN) and **BetMGM** (via Yahoo) — full fields; "
        "**Kalshi** (prediction market, via covers.com) shown as a third reference for the top names.",
        "",
        f"Overrounds before de-vig: DraftKings **{or_dk:.3f}**, BetMGM **{or_mgm:.3f}** (48 teams each).",
        "",
        "| Team | Model | Market (DK+MGM) | Gap (pp) | Model/Market | Kalshi |",
        "|------|------:|----------------:|---------:|-------------:|-------:|",
    ]
    for r in rows:
        gap = f"{r['gap_pp']:+.1f}" if r["gap_pp"] is not None else "—"
        ratio = f"{r['ratio']:.2f}" if r["ratio"] is not None else "—"
        lines.append(f"| {r['team']} | {pct(r['model'])} | {pct(r['market'])} | {gap} | "
                     f"{ratio} | {pct(r['kalshi'])} |")
    lines += [
        "",
        f"Top-2 concentration: **model {top2_model:.0%}** ({top.index[0]} + {top.index[1]}) vs "
        f"**market {top2_market:.0%}**. Top-15 mass: model {mass_model:.2f} vs market {mass_market:.2f}.",
        "",
        "## Read",
        "",
        READ,
        "",
    ]
    out = ROOT / "reports" / "market_check_2026.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    # ---- console echo ----
    print(f"overrounds: DraftKings {or_dk:.3f}, BetMGM {or_mgm:.3f}")
    print(tbl.assign(
        model=lambda d: (d.model * 100).round(1), market=lambda d: (d.market * 100).round(1),
        gap_pp=lambda d: d.gap_pp.round(1), ratio=lambda d: d.ratio.round(2),
    ).to_string(index=False))
    print(f"\ntop-2: model {top2_model:.0%} vs market {top2_market:.0%}; "
          f"top-15 mass model {mass_model:.2f} vs market {mass_market:.2f}")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
