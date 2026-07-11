"""Pydantic v2 schemas shared across the API."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.constants import (
    MAX_PREDICTION_DAYS,
    MIN_ELEVATION_MASK_DEG,
    MAX_ELEVATION_MASK_DEG,
    DEFAULT_ELEVATION_MASK_DEG,
    PRIORITY_LEVELS,
)


# ---------------------------------------------------------------------------
# Ground station
# ---------------------------------------------------------------------------
class GroundStation(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    latitude_deg: float = Field(..., ge=-90, le=90)
    longitude_deg: float = Field(..., ge=-180, le=180)
    altitude_m: float = Field(default=0.0, ge=-500, le=9000)
    min_elevation_deg: float = Field(
        default=DEFAULT_ELEVATION_MASK_DEG,
        ge=MIN_ELEVATION_MASK_DEG,
        le=MAX_ELEVATION_MASK_DEG,
        description="Minimum elevation mask (local obstructions / RF horizon)",
    )


class GroundStationPreset(BaseModel):
    id: str
    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    note: str


# ---------------------------------------------------------------------------
# Satellites / catalogue
# ---------------------------------------------------------------------------
class SatelliteSummary(BaseModel):
    norad_id: int
    name: str
    tle_epoch: Optional[datetime] = None
    source: Literal["live", "demo_archive"]


class DataSourceStatus(BaseModel):
    mode: Literal["live", "demo_archive"]
    provider: str
    last_refreshed: Optional[datetime] = None
    satellite_count: int
    message: str


# ---------------------------------------------------------------------------
# Pass prediction
# ---------------------------------------------------------------------------
class PassPredictionRequest(BaseModel):
    norad_id: int = Field(..., description="NORAD catalogue ID of the satellite")
    ground_station: GroundStation
    start_time_utc: datetime = Field(..., description="Prediction window start, UTC, timezone-aware")
    duration_hours: float = Field(..., gt=0, description="Length of prediction window in hours")

    @field_validator("duration_hours")
    @classmethod
    def _cap_duration(cls, v: float) -> float:
        max_hours = MAX_PREDICTION_DAYS * 24
        if v > max_hours:
            raise ValueError(
                f"duration_hours must not exceed {max_hours} ({MAX_PREDICTION_DAYS} days)"
            )
        return v

    @field_validator("start_time_utc")
    @classmethod
    def _require_tz(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("start_time_utc must be timezone-aware (include UTC offset)")
        return v


class PassEvent(BaseModel):
    aos_utc: datetime
    los_utc: datetime
    max_elevation_utc: datetime
    max_elevation_deg: float
    duration_seconds: float
    aos_azimuth_deg: Optional[float] = None
    los_azimuth_deg: Optional[float] = None
    max_elevation_azimuth_deg: Optional[float] = None
    sunlit_at_max: Optional[bool] = None


class PassPredictionResponse(BaseModel):
    norad_id: int
    satellite_name: str
    ground_station: GroundStation
    data_mode: Literal["live", "demo_archive"]
    window_start_utc: datetime
    window_end_utc: datetime
    passes: List[PassEvent]
    pass_count: int


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------
class CommunicationRequest(BaseModel):
    request_id: str = Field(..., min_length=1, max_length=64)
    norad_id: int
    satellite_name: Optional[str] = None
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    earliest_start_utc: datetime
    latest_end_utc: datetime
    min_elevation_deg: float = Field(default=DEFAULT_ELEVATION_MASK_DEG, ge=0, le=90)
    min_contact_seconds: float = Field(default=60, ge=1)

    @model_validator(mode="after")
    def _check_window(self):
        if self.earliest_start_utc.tzinfo is None or self.latest_end_utc.tzinfo is None:
            raise ValueError("earliest_start_utc and latest_end_utc must be timezone-aware")
        if self.latest_end_utc <= self.earliest_start_utc:
            raise ValueError("latest_end_utc must be after earliest_start_utc")
        return self


class ScheduleGenerationRequest(BaseModel):
    ground_station: GroundStation
    requests: List[CommunicationRequest] = Field(..., min_length=1, max_length=50)


class ScheduledContact(BaseModel):
    request_id: str
    norad_id: int
    satellite_name: Optional[str] = None
    priority: str
    aos_utc: datetime
    los_utc: datetime
    max_elevation_deg: float
    scheduled_start_utc: datetime
    scheduled_end_utc: datetime
    score: float
    reason: str


class RejectedRequest(BaseModel):
    request_id: str
    norad_id: int
    reason: str


class ScheduleResult(BaseModel):
    ground_station: GroundStation
    scheduled: List[ScheduledContact]
    rejected: List[RejectedRequest]
    total_requests: int
    scheduled_count: int
    rejected_count: int
    utilization_seconds: float
    window_start_utc: Optional[datetime] = None
    window_end_utc: Optional[datetime] = None
    utilization_pct: float = 0.0


class ExportFormat(BaseModel):
    format: Literal["json", "csv"] = "json"


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
