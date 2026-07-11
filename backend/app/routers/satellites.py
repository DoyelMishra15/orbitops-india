from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.constants import PRESET_GROUND_STATIONS
from app.models.schemas import DataSourceStatus, GroundStationPreset, SatelliteSummary
from app.services.tle_provider import get_catalogue

router = APIRouter(tags=["satellites"])


@router.get("/satellites", response_model=list[SatelliteSummary])
def list_satellites(q: str | None = None):
    catalogue = get_catalogue()
    records = catalogue.list_satellites()
    if q:
        q_lower = q.lower()
        records = [r for r in records if q_lower in r.name.lower() or q_lower == str(r.norad_id)]
    return [
        SatelliteSummary(norad_id=r.norad_id, name=r.name, source=catalogue.mode)  # type: ignore[arg-type]
        for r in records
    ]


@router.get("/satellites/{norad_id}", response_model=SatelliteSummary)
def get_satellite(norad_id: int):
    catalogue = get_catalogue()
    record = catalogue.get(norad_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Satellite with NORAD ID {norad_id} not found in current data source.")
    return SatelliteSummary(norad_id=record.norad_id, name=record.name, source=catalogue.mode)  # type: ignore[arg-type]


@router.get("/data-source/status", response_model=DataSourceStatus)
def data_source_status():
    catalogue = get_catalogue()
    last_refreshed = (
        datetime.fromtimestamp(catalogue.last_refreshed, tz=timezone.utc)
        if catalogue.last_refreshed
        else None
    )
    message = (
        "Live public orbital elements loaded from Celestrak."
        if catalogue.mode == "live"
        else "Offline demo/archive mode: serving a single scientifically verified reference TLE "
        "(Vanguard 1, NORAD 5). Not live data — see docs/DATA_SOURCES.md."
    )
    return DataSourceStatus(
        mode=catalogue.mode,  # type: ignore[arg-type]
        provider=catalogue.provider,
        last_refreshed=last_refreshed,
        satellite_count=len(catalogue.list_satellites()),
        message=message,
    )


@router.get("/ground-stations/presets", response_model=list[GroundStationPreset])
def ground_station_presets():
    return [GroundStationPreset(**gs) for gs in PRESET_GROUND_STATIONS]
