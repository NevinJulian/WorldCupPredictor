"""Confederation-bias audit: is the model over-rating CONMEBOL on the WC backtest?

    python scripts/confed_audit_2026.py

Analysis only — no model change. Tests the market-check hypothesis (#15/#16: the model over-
rates Spain + CONMEBOL vs the betting market) against the actual walk-forward backtest, and
writes a committed table + read to reports/confed_audit_2026.md.

Part 1 — per-match calibration. For each World Cup 2010-2022, fit the model on everything
before it and predict H/D/A for the finals. Restrict to INTER-confederation matches (the only
games that anchor cross-confederation strength), bucket each side by its confederation, and
compare predicted vs actual expected points (3*win + 1*draw). Run for the Elo-logistic baseline
(elo_diff only) and the ensemble — if both miscalibrate the same way, it is an Elo-rating effect.

Part 2 — Elo drift. Mean pre-WC Elo of WC participants by confederation per year, and the
CONMEBOL-vs-UEFA head-to-head win-share vs the Elo-implied win probability by era — does the
Elo edge outrun the results that should anchor it?
"""
import pathlib
import sys
import warnings
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from wcpred import DATA_PROCESSED, datasets, models  # noqa: E402

YEARS = (2010, 2014, 2018, 2022)

READ = """\
**Verdict: defensible disagreement with the market — keep it (monitor, don't fix).**

1. **No backtested CONMEBOL over-rating — the opposite.** On the 2010-2022 WC backtest the model
   slightly *under*-predicts CONMEBOL (actual 1.82 expected-points/game vs 1.71-1.80 predicted)
   and UEFA (1.69 vs 1.57-1.63) in inter-confederation matches. The only buckets it over-predicts
   are the weaker AFC (+0.13) and CONCACAF (+0.19) — opposite to the market narrative. The
   Elo-logistic baseline shows the same shape, so it is an Elo-rating effect, not a GBM artifact.
2. **Elo isn't drifting high enough to matter.** CONMEBOL's mean-Elo edge over UEFA among WC teams
   grew (+49 in 2010 to +91 in 2022), but the CONMEBOL-vs-UEFA head-to-head only under-delivers the
   Elo expectation by ~1pp (1990-2017), widening to ~3.6pp win-share in 2018-2026 — within sampling
   noise (n=81). A mild recent drift to watch, not a measurable bias.
3. **So the model's CONMEBOL/Spain confidence is earned at World Cups; the market is just more
   bearish** (host conditions, squad age, risk premia it prices that the model can't see). The
   title-level over-concentration vs the market (top-2 47% vs 24%) is better explained by iid-sim
   under-dispersion — and possibly intra-bucket top-team concentration (e.g. Argentina, which a
   confederation average can't isolate) — than by a confederation rating bias. No fix warranted."""


def part1_calibration(feat: pd.DataFrame) -> pd.DataFrame:
    """Predicted vs actual expected-points by confederation, inter-confederation WC matches."""
    def audit(make_model):
        agg = defaultdict(lambda: {"n": 0, "pred": 0.0, "act": 0.0})
        for y in YEARS:
            train, test = datasets.tournament_holdout(feat, y)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                proba = make_model().fit(train).predict_proba(test)
            for (_, r), (pH, pD, pA) in zip(test.iterrows(), proba):
                ch, ca = r["home_confed"], r["away_confed"]
                if pd.isna(ch) or pd.isna(ca) or ch == ca:
                    continue
                res = r["result"]
                agg[ch]["n"] += 1
                agg[ch]["pred"] += 3 * pH + pD
                agg[ch]["act"] += 3 if res == "H" else 1 if res == "D" else 0
                agg[ca]["n"] += 1
                agg[ca]["pred"] += 3 * pA + pD
                agg[ca]["act"] += 3 if res == "A" else 1 if res == "D" else 0
        return agg

    elo = audit(models.EloLogisticModel)
    ens = audit(models.EnsembleModel)
    rows = []
    for c in sorted(ens, key=lambda c: -ens[c]["n"]):
        n = ens[c]["n"]
        rows.append({
            "confed": c, "n": n,
            "elo_pred_ppg": elo[c]["pred"] / n, "ens_pred_ppg": ens[c]["pred"] / n,
            "actual_ppg": ens[c]["act"] / n, "ens_gap": (ens[c]["pred"] - ens[c]["act"]) / n,
            "se": 1.5 / np.sqrt(n),
        })
    return pd.DataFrame(rows)


def part2_elo_by_year(feat: pd.DataFrame) -> pd.DataFrame:
    """Mean pre-WC Elo of WC participants, CONMEBOL vs UEFA, per tournament year."""
    rows = []
    for y in YEARS:
        _, test = datasets.tournament_holdout(feat, y)
        long = pd.DataFrame(
            [(r["home_team"], r["home_confed"], r["elo_home"], r["date"]) for _, r in test.iterrows()] +
            [(r["away_team"], r["away_confed"], r["elo_away"], r["date"]) for _, r in test.iterrows()],
            columns=["team", "confed", "elo", "date"],
        ).sort_values("date").groupby("team").first()
        con, uefa = long[long.confed == "CONMEBOL"]["elo"], long[long.confed == "UEFA"]["elo"]
        rows.append({"year": y, "conmebol_elo": con.mean(), "uefa_elo": uefa.mean(),
                     "gap": con.mean() - uefa.mean(), "n_con": len(con), "n_uefa": len(uefa)})
    return pd.DataFrame(rows)


def part2_h2h(feat: pd.DataFrame) -> pd.DataFrame:
    """CONMEBOL-vs-UEFA head-to-head win-share, actual vs Elo-implied, by era."""
    m = feat[(((feat.home_confed == "CONMEBOL") & (feat.away_confed == "UEFA")) |
              ((feat.home_confed == "UEFA") & (feat.away_confed == "CONMEBOL"))) & feat.played].copy()

    def con_winshare(r):
        if r["result"] == "D":
            return 0.5
        con_home = r["home_confed"] == "CONMEBOL"
        con_win = (r["result"] == "H" and con_home) or (r["result"] == "A" and not con_home)
        return 1.0 if con_win else 0.0

    def con_elo_p(r):
        d = (r["elo_home"] - r["elo_away"]) if r["home_confed"] == "CONMEBOL" else (r["elo_away"] - r["elo_home"])
        return 1.0 / (1.0 + 10 ** (-d / 400))

    m["ws"] = m.apply(con_winshare, axis=1)
    m["elo_p"] = m.apply(con_elo_p, axis=1)
    rows = []
    for lo, hi, lab in [(1990, 2010, "1990-2009"), (2010, 2018, "2010-2017"), (2018, 2027, "2018-2026")]:
        sub = m[(m.year >= lo) & (m.year < hi)]
        if len(sub):
            rows.append({"era": lab, "n": len(sub), "actual_ws": sub["ws"].mean(),
                         "elo_ws": sub["elo_p"].mean(), "gap": sub["ws"].mean() - sub["elo_p"].mean()})
    return pd.DataFrame(rows)


def main() -> int:
    fp = DATA_PROCESSED / "match_features.parquet"
    if not fp.exists():
        raise SystemExit(f"{fp} not found. Run scripts/02_build_features.py first.")
    feat = pd.read_parquet(fp)

    cal = part1_calibration(feat)
    elo_year = part2_elo_by_year(feat)
    h2h = part2_h2h(feat)

    lines = [
        "# WC 2026 — confederation-bias audit (is the model over-rating CONMEBOL?)",
        "",
        "*Analysis only (no model change). Backtest: walk-forward World Cups 2010-2022.*",
        "",
        "## Part 1 — per-match calibration (inter-confederation WC matches)",
        "Predicted vs actual **expected points per game** (3·win + 1·draw), each side bucketed by "
        "its confederation. `~1SE` is a rough one-sigma band on the actual rate.",
        "",
        "| Confed | n | Elo-base pred | Ensemble pred | Actual | Ensemble gap | ~1SE |",
        "|--------|--:|--------------:|--------------:|-------:|-------------:|-----:|",
    ]
    for _, r in cal.iterrows():
        lines.append(f"| {r.confed} | {int(r.n)} | {r.elo_pred_ppg:.2f} | {r.ens_pred_ppg:.2f} | "
                     f"{r.actual_ppg:.2f} | {r.ens_gap:+.2f} | {r.se:.2f} |")
    lines += [
        "",
        "*(gap > 0 = model over-predicts that confederation; gap < 0 = under-predicts.)*",
        "",
        "## Part 2 — Elo drift, CONMEBOL vs UEFA",
        "**(a) Mean pre-WC Elo of World Cup participants:**",
        "",
        "| Year | CONMEBOL | UEFA | Gap | n (CON/UEFA) |",
        "|------|---------:|-----:|----:|:------------:|",
    ]
    for _, r in elo_year.iterrows():
        lines.append(f"| {int(r.year)} | {r.conmebol_elo:.0f} | {r.uefa_elo:.0f} | "
                     f"{r.gap:+.0f} | {int(r.n_con)}/{int(r.n_uefa)} |")
    lines += [
        "",
        "**(b) CONMEBOL-vs-UEFA head-to-head win-share (win=1, draw=0.5, loss=0) vs the "
        "Elo-implied win probability:**",
        "",
        "| Era | n | Actual | Elo-implied | Actual − Elo |",
        "|-----|--:|-------:|------------:|-------------:|",
    ]
    for _, r in h2h.iterrows():
        lines.append(f"| {r.era} | {int(r.n)} | {r.actual_ws:.3f} | {r.elo_ws:.3f} | {r.gap:+.3f} |")
    lines += ["", "## Read", "", READ, ""]

    out = ROOT / "reports" / "confed_audit_2026.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    print("Part 1 — calibration (inter-confederation WC matches):")
    print(cal.to_string(index=False))
    print("\nPart 2a — mean pre-WC Elo by confederation:")
    print(elo_year.to_string(index=False))
    print("\nPart 2b — CONMEBOL vs UEFA head-to-head:")
    print(h2h.to_string(index=False))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
