from datetime import datetime, timedelta, timezone

import pytest

from app.services.pass_predictor import predict_passes, PassPredictionError
from app.services.tle_provider import TleRecord

# The standard SGP4 verification TLE (Vanguard 1 / NORAD 5), epoch 2000.
# Same fixture shipped in app/data/demo_tles.txt.
VANGUARD_1 = TleRecord(
    norad_id=5,
    name="VANGUARD 1 (SGP4 REFERENCE VECTOR)",
    line1="1 00005U 58002B   00179.78495062  .00000023  00000-0  28098-4 0  4753",
    line2="2 00005  34.2682 348.7242 1859667 331.7664  19.3264 10.82419157413667",
)


def test_predict_passes_returns_list_within_window():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    passes = predict_passes(
        tle=VANGUARD_1,
        latitude_deg=20.2961,
        longitude_deg=85.8245,
        altitude_m=45.0,
        min_elevation_deg=10.0,
        start_time_utc=start,
        duration_hours=48.0,
    )
    assert isinstance(passes, list)
    for p in passes:
        assert start <= p.aos_utc <= start + timedelta(hours=48)
        assert p.los_utc > p.aos_utc
        assert p.max_elevation_deg >= 10.0
        assert p.duration_seconds > 0


def test_predict_passes_rejects_naive_datetime():
    naive_start = datetime(2026, 1, 1)
    with pytest.raises(PassPredictionError):
        predict_passes(
            tle=VANGUARD_1,
            latitude_deg=20.0,
            longitude_deg=85.0,
            altitude_m=0.0,
            min_elevation_deg=10.0,
            start_time_utc=naive_start,
            duration_hours=24.0,
        )


def test_higher_elevation_mask_yields_fewer_or_equal_passes():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    low_mask = predict_passes(
        tle=VANGUARD_1,
        latitude_deg=20.2961,
        longitude_deg=85.8245,
        altitude_m=45.0,
        min_elevation_deg=5.0,
        start_time_utc=start,
        duration_hours=72.0,
    )
    high_mask = predict_passes(
        tle=VANGUARD_1,
        latitude_deg=20.2961,
        longitude_deg=85.8245,
        altitude_m=45.0,
        min_elevation_deg=60.0,
        start_time_utc=start,
        duration_hours=72.0,
    )
    assert len(high_mask) <= len(low_mask)


def test_pass_events_are_time_ordered():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    passes = predict_passes(
        tle=VANGUARD_1,
        latitude_deg=20.2961,
        longitude_deg=85.8245,
        altitude_m=45.0,
        min_elevation_deg=10.0,
        start_time_utc=start,
        duration_hours=72.0,
    )
    for a, b in zip(passes, passes[1:]):
        assert a.los_utc <= b.aos_utc
