"""
Satellite pass prediction engine.

Uses Skyfield (which wraps the SGP4 propagator) to compute rise / culminate
/ set events for a satellite as seen from a ground station, over a bounded
time window.

METHODOLOGY (see docs/METHODOLOGY.md for full detail):
    1. Build an EarthSatellite from the TLE (SGP4 propagation).
    2. Build a topocentric observer (WGS84 lat/lon/altitude) for the
       ground station.
    3. Use Skyfield's `find_events` to locate AOS (rise through the
       elevation mask), maximum-elevation (culminate), and LOS (set below
       the elevation mask) events across the window.
    4. Compute azimuth at each event via topocentric alt/az.

LIMITATIONS (documented, not hidden):
    - SGP4/TLE accuracy degrades with time-since-epoch; predictions using
      stale TLEs (days-to-weeks old, or the offline demo fixture) should be
      treated as indicative, not operational.
    - Atmospheric refraction, ionospheric effects and local RF obstructions
      are not modelled; the elevation mask is a simple geometric cutoff.
    - No solar-illumination ("sunlit") computation is performed in the MVP —
      that requires an additional planetary ephemeris file (~15-30 MB),
      which was intentionally left out to keep the deployment lightweight.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from skyfield.api import EarthSatellite, load, wgs84

from app.core.constants import DEFAULT_MIN_CONTACT_SECONDS
from app.models.schemas import PassEvent
from app.services.tle_provider import TleRecord

_ts = load.timescale()


class PassPredictionError(Exception):
    pass


def predict_passes(
    tle: TleRecord,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float,
    min_elevation_deg: float,
    start_time_utc: datetime,
    duration_hours: float,
    min_contact_seconds: float = DEFAULT_MIN_CONTACT_SECONDS,
) -> List[PassEvent]:
    """Compute all passes of `tle`'s satellite above `min_elevation_deg`
    as seen from the given ground station, within
    [start_time_utc, start_time_utc + duration_hours]."""

    if start_time_utc.tzinfo is None:
        raise PassPredictionError("start_time_utc must be timezone-aware")

    satellite = EarthSatellite(tle.line1, tle.line2, tle.name, _ts)
    observer = wgs84.latlon(latitude_deg, longitude_deg, elevation_m=altitude_m)

    t0 = _ts.from_datetime(start_time_utc.astimezone(timezone.utc))
    end_time = start_time_utc + timedelta(hours=duration_hours)
    t1 = _ts.from_datetime(end_time.astimezone(timezone.utc))

    try:
        times, events = satellite.find_events(
            observer, t0, t1, altitude_degrees=min_elevation_deg
        )
    except Exception as exc:  # noqa: BLE001
        raise PassPredictionError(f"Propagation failed: {exc}") from exc

    difference = satellite - observer

    passes: List[PassEvent] = []
    current_aos = None
    current_aos_az = None
    max_elev = None
    max_elev_t = None
    max_elev_az = None

    for t, event in zip(times, events):
        if event == 0:  # rise / AOS
            current_aos = t
            alt, az, _ = difference.at(t).altaz()
            current_aos_az = az.degrees
            max_elev, max_elev_t, max_elev_az = None, None, None
        elif event == 1:  # culminate / max elevation
            alt, az, _ = difference.at(t).altaz()
            max_elev = alt.degrees
            max_elev_t = t
            max_elev_az = az.degrees
        elif event == 2:  # set / LOS
            if current_aos is None:
                # Window started mid-pass; skip incomplete leading pass.
                continue
            los_t = t
            alt, az, _ = difference.at(los_t).altaz()
            los_az = az.degrees

            aos_dt = current_aos.utc_datetime()
            los_dt = los_t.utc_datetime()
            duration_s = (los_dt - aos_dt).total_seconds()

            if duration_s >= min_contact_seconds and max_elev_t is not None:
                passes.append(
                    PassEvent(
                        aos_utc=aos_dt,
                        los_utc=los_dt,
                        max_elevation_utc=max_elev_t.utc_datetime(),
                        max_elevation_deg=round(max_elev, 2),
                        duration_seconds=round(duration_s, 1),
                        aos_azimuth_deg=round(current_aos_az, 2) if current_aos_az is not None else None,
                        los_azimuth_deg=round(los_az, 2),
                        max_elevation_azimuth_deg=round(max_elev_az, 2) if max_elev_az is not None else None,
                        sunlit_at_max=None,  # not computed in MVP (see module docstring)
                    )
                )
            current_aos = None

    return passes
