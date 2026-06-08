"""Download raw data into data/raw/.

    python scripts/01_download.py             # core tier (no API key)
    python scripts/01_download.py --advanced  # also scrape squad value / injuries (Transfermarkt)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wcpred import download  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(download.main(sys.argv[1:]))
