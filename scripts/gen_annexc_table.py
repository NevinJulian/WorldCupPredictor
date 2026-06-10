"""(Re)generate config/annexc_r32.csv — FIFA's Annex C round-of-32 third-place allocation.

Run once (needs network):

    python scripts/gen_annexc_table.py

The 2026 World Cup advances the 8 best third-placed teams (of 12 groups) into the round of
32; which group's third fills which R32 slot depends on *which* eight groups' thirds qualify —
the 495-combination table (C(12,8)) published in Annex C of the FWC2026 Regulations. We parse
it from the Wikipedia template that reproduces Annex C, hard-validate every row, and vendor it
to a static CSV the simulator loads (so the sim and tests never touch the network).

Output columns: `thirds` (the 8-letter sorted combination of qualifying third groups) plus one
column per group winner that faces a third — A,B,D,E,G,I,K,L — giving the GROUP letter of the
third-placed team that winner plays. Validation checks: 495 rows = all C(12,8) combinations;
each row is a bijection (the 8 assigned thirds are exactly the qualifying set); and every
assignment respects that match's published list of eligible third groups.
"""
import csv
import itertools
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = ("https://en.wikipedia.org/w/index.php"
       "?title=Template:2026_FIFA_World_Cup_third-place_table&action=raw")

# The 8 group winners that face a third-placed team, in the table's column order
# (Matches 79/85/81/74/82/77/87/80 -> winners A/B/D/E/G/I/K/L).
COLS = ["A", "B", "D", "E", "G", "I", "K", "L"]
# Each winner's published list of eligible third-place groups (from the R32 schedule).
ALLOWED = {
    "A": set("CEFHI"), "B": set("EFGIJ"), "D": set("BEFIJ"), "E": set("ABCDF"),
    "G": set("AEHIJ"), "I": set("CDFGH"), "K": set("DEIJL"), "L": set("EHIJK"),
}


def parse(txt: str) -> dict[int, tuple[list[str], list[str]]]:
    """Parse the wikitable into {row_no: (advancing_groups, assigned_thirds)}."""
    rows: dict[int, tuple[list[str], list[str]]] = {}
    for block in txt.split("|-"):
        m = re.search(r'scope="row"\s*\|\s*(\d+)', block)
        if not m:
            continue
        advancing = re.findall(r"'''([A-L])'''", block)      # bold = that group's third qualifies
        assigned = re.findall(r"\b3([A-L])\b", block)         # the 8 third-slot assignments
        if len(advancing) == 8 and len(assigned) == 8:
            rows[int(m.group(1))] = (advancing, assigned)
    return rows


def validate(rows: dict[int, tuple[list[str], list[str]]]) -> None:
    assert len(rows) == 495, f"expected 495 rows, got {len(rows)}"
    all_combinations = {frozenset(c) for c in itertools.combinations("ABCDEFGHIJKL", 8)}
    seen = set()
    for no, (advancing, assigned) in rows.items():
        combo = frozenset(advancing)
        assert len(combo) == 8, f"row {no}: not 8 distinct groups"
        assert frozenset(assigned) == combo, f"row {no}: assignments are not a bijection"
        for col, third in zip(COLS, assigned):
            assert third in ALLOWED[col], f"row {no}: 3{third} ineligible for winner {col}"
        seen.add(combo)
    assert seen == all_combinations, "rows do not cover all C(12,8) combinations"


def main() -> int:
    print(f"Fetching Annex C table from {URL} ...")
    # Wikipedia rejects the default urllib User-Agent (403); send a descriptive one.
    req = urllib.request.Request(URL, headers={
        "User-Agent": "WorldCupPredictor/1.0 (annex-c table generator; https://github.com/NevinJulian/WorldCupPredictor)"
    })
    txt = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    rows = parse(txt)
    validate(rows)
    out = ROOT / "config" / "annexc_r32.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["thirds"] + COLS)
        for no in sorted(rows):
            advancing, assigned = rows[no]
            writer.writerow(["".join(sorted(advancing))] + assigned)
    print(f"Wrote {out} (495 rows, validated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
