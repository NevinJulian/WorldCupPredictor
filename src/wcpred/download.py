"""Download raw data sources into data/raw/.

Run on YOUR machine (it makes outbound HTTP requests):

    python scripts/01_download.py            # core tier
    python scripts/01_download.py --advanced # also scrape squad value / injuries

Core tier needs no API key. The advanced tier hits Transfermarkt and is delegated to
`wcpred.squad` (rate-limited, ToS-sensitive).
"""
from __future__ import annotations

import io
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import yaml

from . import CONFIG_DIR, DATA_RAW

USER_AGENT = "WorldCupPredictor/0.1 (research; contact: you@example.com)"
TIMEOUT = 30


def load_sources(path: Path | None = None) -> dict:
    path = path or (CONFIG_DIR / "sources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _get(session: requests.Session, url: str, retries: int = 3, backoff: float = 2.0) -> bytes:
    """GET with retries on transient errors. A 4xx (e.g. a dead mirror's 404) fails fast so the
    caller can move straight to the next mirror instead of retrying a permanent error."""
    last = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            return r.content
        except requests.HTTPError as e:  # pragma: no cover - network
            status = getattr(e.response, "status_code", None)
            if status is not None and 400 <= status < 500:
                raise RuntimeError(f"{url}: {status} client error (not retrying)") from e
            last = e
            print(f"  attempt {attempt}/{retries} failed: {e}")
            time.sleep(backoff ** attempt)
        except requests.RequestException as e:  # pragma: no cover - network
            last = e
            print(f"  attempt {attempt}/{retries} failed: {e}")
            time.sleep(backoff ** attempt)
    raise RuntimeError(f"Failed to download {url}: {last}")


def _save_csv(content: bytes, dest: Path) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    print(f"  saved {dest.name}: {len(df):,} rows, {len(df.columns)} cols")
    return df


def download_core(sources: dict | None = None, out_dir: Path | None = None) -> dict[str, Path]:
    """Fetch results / goalscorers / shootouts / former_names + FIFA ranking."""
    sources = sources or load_sources()
    out_dir = out_dir or DATA_RAW
    session = _session()
    paths: dict[str, Path] = {}

    print("Downloading core match data (martj42/international_results)...")
    for key in ("results", "goalscorers", "shootouts", "former_names"):
        url = sources["core"][key]["url"]
        dest = out_dir / f"{key}.csv"
        _save_csv(_get(session, url), dest)
        paths[key] = dest

    print("Downloading FIFA world ranking (trying mirrors)...")
    dest = out_dir / "fifa_ranking.csv"
    for url in sources["core"]["fifa_ranking"]["urls"]:
        try:
            _save_csv(_get(session, url), dest)
            paths["fifa_ranking"] = dest
            break
        except Exception as e:  # try next mirror
            print(f"  mirror failed ({url}): {e}")
    else:
        print("  WARNING: all FIFA-ranking mirrors failed; pipeline will skip rank features.")

    return paths


def download_advanced(out_dir: Path | None = None) -> None:
    """Squad market value + injuries (modern subset). Delegated to wcpred.squad."""
    from . import squad

    out_dir = out_dir or DATA_RAW
    print("Downloading ADVANCED features (squad value / injuries) — be patient & polite...")
    squad.scrape_all(out_dir)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    download_core()
    if "--advanced" in argv:
        download_advanced()
    print("Done. Raw data in", DATA_RAW)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
