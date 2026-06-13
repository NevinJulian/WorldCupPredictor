"""One-command matchday refresh — keep the LIVE WC-2026 forecast tracking played results.

    python scripts/10_refresh.py                 # download latest data, rebuild, regenerate live forecast/export
    python scripts/10_refresh.py --no-download    # use the raw data already on disk (offline / CI)
    python scripts/10_refresh.py --sims N          # Monte-Carlo N for the forecast record (default 50000)

The model is UNCHANGED (v0.4.0). As WC games are played, martj42 fills in their scores; a played WC
result carries the top Elo K (60) and feeds the as-of features, so simply re-running the existing
chain nudges the remaining predictions from results. Leakage-safe by construction — only played
matches inform later-match predictions (the 5y Dixon-Coles half-life keeps DC strengths from
over-reacting to a handful of games: a heavy, correct prior).

Chain: snapshot the pre-tournament forecast (once, immutable) -> download -> rebuild features ->
regenerate forecast_2026.{json,md} -> scoreline_distribution_2026.md -> model_export.json -> verify
invariants (title -> 1.0, advance -> 32.0) and print tournament progress.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import refresh  # noqa: E402

SCRIPTS = ROOT / "scripts"


def _run(script: str, extra: list[str] | None = None) -> None:
    """Run a pipeline script in a fresh interpreter (each is self-anchoring, CWD-independent)."""
    extra = extra or []
    print(f"\n=== {script} {' '.join(extra)} ===".rstrip())
    subprocess.run([sys.executable, str(SCRIPTS / script), *extra], check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Matchday refresh of the live WC-2026 forecast.")
    ap.add_argument("--no-download", action="store_true",
                    help="skip the data download; use the raw CSVs already on disk")
    ap.add_argument("--sims", type=int, default=None,
                    help="Monte-Carlo N for the forecast record (default 50000)")
    args = ap.parse_args()

    # 0. Preserve the pristine pre-tournament forecast, ONCE, before refreshing anything.
    if refresh.snapshot_pretournament():
        print(f"Snapshotted pre-tournament forecast -> {refresh.PRETOURNAMENT_JSON.name} "
              f"+ {refresh.PRETOURNAMENT_MD.name} (immutable; never overwritten).")
    else:
        print("Pre-tournament snapshot already exists — preserved.")

    # 1. Latest data (WC scores fill in here as games are played).
    if args.no_download:
        print("\n(skipping download; using the raw data already on disk)")
    else:
        _run("01_download.py")

    # 2-5. Rebuild the processed table, then regenerate the live forecast + reports + web export.
    _run("02_build_features.py")
    _run("forecast_experiment_2026.py", [] if args.sims is None else ["--sims", str(args.sims)])
    _run("scoreline_distribution_2026.py")
    _run("09_export_web.py")

    # 6. Re-verify invariants and report tournament progress.
    fc = json.loads(refresh.LIVE_JSON.read_text(encoding="utf-8"))
    md = fc["metadata"]
    title = sum(t["title"] for t in fc["teams"])
    adv = sum(t["advance"] for t in fc["teams"])
    print("\n=== refresh complete ===")
    print(f"  model v{md['model_version']}  as-of {md['as_of']}  "
          f"WC-2026 played {md.get('wc2026_matches_played', '?')} / total played {md.get('matches_played', '?')}")
    print(f"  invariants: title sum {title:.6f} (-> 1.0), advance sum {adv:.6f} (-> 32.0)")
    if not (abs(title - 1.0) < 1e-4 and abs(adv - 32.0) < 1e-3):
        print("  INVARIANT CHECK FAILED", file=sys.stderr)
        return 1
    top = ", ".join(f"{t['team']} {t['title'] * 100:.1f}%" for t in fc["teams"][:3])
    print(f"  top title odds: {top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
