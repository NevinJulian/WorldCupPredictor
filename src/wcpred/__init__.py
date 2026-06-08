"""World Cup Predictor — international football match & tournament modelling.

Pipeline order:
    download  ->  clean  ->  elo (+features)  ->  datasets  ->  (models)  ->  tournament

See PLAN.md for the design rationale.
"""
from __future__ import annotations

from pathlib import Path

__version__ = "0.1.0"

# Repo-root-relative paths so the package works regardless of CWD.
PKG_DIR = Path(__file__).resolve().parent
ROOT = PKG_DIR.parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
CONFIG_DIR = ROOT / "config"

for _p in (DATA_RAW, DATA_PROCESSED):
    _p.mkdir(parents=True, exist_ok=True)
