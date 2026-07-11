"""
Pure-Python validation helpers.

Kept dependency-free (no FastAPI / Pydantic imports) so this module can be
unit-tested in any environment, including ones without the web dependencies
installed.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.constants import (
    MAX_PREDICTION_DAYS,
    MIN_PREDICTION_HOURS,
    MIN_ELEVATION_MASK_DEG,
    MAX_ELEVATION_MASK_DEG,
)


class ValidationError(Exception):
    """Raised when domain-level validation fails."""


def validate_latitude(lat: float) -> float:
    if lat is None or not (-90.0 <= lat <= 90.0):
        raise ValidationError(f"Latitude must be between -90 and 90 degrees, got {lat}")
    return lat


def validate_longitude(lon: float) -> float:
    if lon is None or not (-180.0 <= lon <= 180.0):
        raise ValidationError(f"Longitude must be between -180 and 180 degrees, got {lon}")
    return lon


def validate_altitude(alt_m: float) -> float:
    if alt_m is None or not (-500.0 <= alt_m <= 9000.0):
        raise ValidationError(f"Altitude must be between -500 and 9000 metres, got {alt_m}")
    return alt_m


def validate_elevation_mask(mask_deg: float) -> float:
    if mask_deg is None or not (MIN_ELEVATION_MASK_DEG <= mask_deg <= MAX_ELEVATION_MASK_DEG):
        raise ValidationError(
            f"Elevation mask must be between {MIN_ELEVATION_MASK_DEG} and "
            f"{MAX_ELEVATION_MASK_DEG} degrees, got {mask_deg}"
        )
    return mask_deg


def validate_time_window(start: datetime, duration_hours: float) -> None:
    if start is None:
        raise ValidationError("Start time is required")
    if start.tzinfo is None:
        raise ValidationError("Start time must be timezone-aware (UTC)")
    if duration_hours is None or duration_hours <= 0:
        raise ValidationError("Duration must be a positive number of hours")
    if duration_hours < MIN_PREDICTION_HOURS:
        raise ValidationError(
            f"Duration must be at least {MIN_PREDICTION_HOURS} hours, got {duration_hours}"
        )
    max_hours = MAX_PREDICTION_DAYS * 24
    if duration_hours > max_hours:
        raise ValidationError(
            f"Duration must not exceed {max_hours} hours "
            f"({MAX_PREDICTION_DAYS} days) to keep computation lightweight, got {duration_hours}"
        )


def validate_time_range_not_absurdly_old(start: datetime, max_days_in_past: int = 365) -> None:
    """Guard against pathological requests for predictions far in the past,
    which are not useful for operational scheduling and waste compute."""
    now = datetime.now(timezone.utc)
    if start < now - timedelta(days=max_days_in_past):
        raise ValidationError(
            f"Start time is more than {max_days_in_past} days in the past; "
            "TLE accuracy degrades severely over such intervals."
        )


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
