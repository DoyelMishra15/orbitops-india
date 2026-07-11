from datetime import datetime, timedelta, timezone

import pytest

from app.core.validation import (
    ValidationError,
    validate_latitude,
    validate_longitude,
    validate_altitude,
    validate_elevation_mask,
    validate_time_window,
    validate_time_range_not_absurdly_old,
)


def test_valid_latitude():
    assert validate_latitude(20.29) == 20.29


@pytest.mark.parametrize("lat", [-91, 91, 200, -200])
def test_invalid_latitude(lat):
    with pytest.raises(ValidationError):
        validate_latitude(lat)


def test_valid_longitude():
    assert validate_longitude(85.82) == 85.82


@pytest.mark.parametrize("lon", [-181, 181, 400])
def test_invalid_longitude(lon):
    with pytest.raises(ValidationError):
        validate_longitude(lon)


def test_valid_altitude():
    assert validate_altitude(216.0) == 216.0


@pytest.mark.parametrize("alt", [-1000, 20000])
def test_invalid_altitude(alt):
    with pytest.raises(ValidationError):
        validate_altitude(alt)


def test_valid_elevation_mask():
    assert validate_elevation_mask(10.0) == 10.0


@pytest.mark.parametrize("mask", [-5, 50, 90])
def test_invalid_elevation_mask(mask):
    with pytest.raises(ValidationError):
        validate_elevation_mask(mask)


def test_valid_time_window():
    start = datetime.now(timezone.utc)
    validate_time_window(start, 24.0)  # should not raise


def test_time_window_requires_tz():
    naive = datetime.now()
    with pytest.raises(ValidationError):
        validate_time_window(naive, 1.0)


def test_time_window_rejects_zero_duration():
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        validate_time_window(start, 0)


def test_time_window_rejects_excessive_duration():
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        validate_time_window(start, 24 * 30)  # 30 days, exceeds MAX_PREDICTION_DAYS


def test_time_window_rejects_too_short_duration():
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        validate_time_window(start, 0.01)


def test_time_range_not_absurdly_old():
    old_start = datetime.now(timezone.utc) - timedelta(days=1000)
    with pytest.raises(ValidationError):
        validate_time_range_not_absurdly_old(old_start)


def test_time_range_recent_is_fine():
    recent_start = datetime.now(timezone.utc) - timedelta(days=1)
    validate_time_range_not_absurdly_old(recent_start)  # should not raise
