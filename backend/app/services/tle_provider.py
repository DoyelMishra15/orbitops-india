"""
Orbital-element (TLE) provider.

Two modes:

LIVE MODE
    Fetches current, legitimate public two-line element sets from Celestrak
    (https://celestrak.org), a widely used, freely available catalogue of
    orbital elements. Results are cached in-process for TLE_CACHE_TTL_SECONDS
    to keep the app lightweight and to avoid hammering the upstream service.

DEMO / ARCHIVE MODE (automatic fallback)
    If live fetch fails (no network, upstream unavailable, timeout) or
    FORCE_DEMO_MODE is set, the app falls back to a small local fixture
    (see app/data/demo_tles.txt) containing one scientifically verified
    reference TLE. This keeps the full pipeline demonstrable offline while
    being explicit that it is not live/current data.

No orbital data is ever fabricated. Every value served either comes from
Celestrak's public feed or from the documented, citation-backed fixture.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from app.config import get_settings
from app.core.constants import MAX_SATELLITES_PER_TLE_LOAD

logger = logging.getLogger("orbitops.tle_provider")

DEMO_TLE_PATH = Path(__file__).resolve().parent.parent / "data" / "demo_tles.txt"

# A small, well-known set of public Celestrak "GROUP" catalogues relevant to
# university / amateur / CubeSat operations. These are just query parameters
# against Celestrak's public GP API — no restricted or private data.
CELESTRAK_GROUPS = ["cubesat", "amateur", "stations"]


@dataclass
class TleRecord:
    norad_id: int
    name: str
    line1: str
    line2: str
    epoch: Optional[str] = None


class TleCatalogue:
    def __init__(self) -> None:
        self._records: dict[int, TleRecord] = {}
        self._mode: str = "demo_archive"
        self._last_refreshed: Optional[float] = None
        self._provider: str = "local fixture (offline)"

    # -- public API ---------------------------------------------------
    @property
    def mode(self) -> str:
        return self._mode

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def last_refreshed(self) -> Optional[float]:
        return self._last_refreshed

    def list_satellites(self) -> list[TleRecord]:
        return list(self._records.values())[:MAX_SATELLITES_PER_TLE_LOAD]

    def get(self, norad_id: int) -> Optional[TleRecord]:
        return self._records.get(norad_id)

    def refresh(self, force: bool = False) -> None:
        settings = get_settings()
        now = time.time()

        if (
            not force
            and self._last_refreshed is not None
            and (now - self._last_refreshed) < settings.TLE_CACHE_TTL_SECONDS
        ):
            return  # cache still fresh

        if settings.FORCE_DEMO_MODE:
            self._load_demo()
            return

        try:
            self._load_live()
        except Exception as exc:  # noqa: BLE001 — any network/parse failure -> fallback
            logger.warning("Live TLE fetch failed (%s); falling back to demo/archive mode.", exc)
            self._load_demo()

    # -- internals ------------------------------------------------------
    def _load_live(self) -> None:
        settings = get_settings()
        records: dict[int, TleRecord] = {}

        with httpx.Client(timeout=settings.TLE_FETCH_TIMEOUT_SECONDS) as client:
            for group in CELESTRAK_GROUPS:
                resp = client.get(
                    settings.CELESTRAK_BASE_URL,
                    params={"GROUP": group, "FORMAT": "tle"},
                )
                resp.raise_for_status()
                records.update(self._parse_tle_text(resp.text))

        if not records:
            raise RuntimeError("Live TLE fetch returned zero satellites")

        self._records = records
        self._mode = "live"
        self._provider = "Celestrak (celestrak.org) public GP catalogue"
        self._last_refreshed = time.time()
        logger.info("Loaded %d satellites from Celestrak (live mode).", len(records))

    def _load_demo(self) -> None:
        text = DEMO_TLE_PATH.read_text(encoding="utf-8")
        self._records = self._parse_tle_text(text)
        self._mode = "demo_archive"
        self._provider = "Local archived fixture (SGP4 reference vector, offline demo mode)"
        self._last_refreshed = time.time()
        logger.info("Loaded %d satellite(s) from demo/archive fixture.", len(self._records))

    @staticmethod
    def _parse_tle_text(text: str) -> dict[int, TleRecord]:
        lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
        records: dict[int, TleRecord] = {}
        i = 0
        while i < len(lines) - 2:
            name, l1, l2 = lines[i].strip(), lines[i + 1], lines[i + 2]
            if l1.startswith("1 ") and l2.startswith("2 "):
                try:
                    norad_id = int(l1[2:7])
                except ValueError:
                    i += 1
                    continue
                records[norad_id] = TleRecord(norad_id=norad_id, name=name, line1=l1, line2=l2)
                i += 3
            else:
                i += 1
        return records


_catalogue: Optional[TleCatalogue] = None


def get_catalogue() -> TleCatalogue:
    global _catalogue
    if _catalogue is None:
        _catalogue = TleCatalogue()
    _catalogue.refresh()
    return _catalogue
