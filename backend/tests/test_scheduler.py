from datetime import datetime, timedelta, timezone

import pytest

from app.models.schemas import PassEvent
from app.services.scheduler import Opportunity, _weighted_interval_schedule, _score
from app.models.schemas import CommunicationRequest


def _mk_pass(start_offset_min: int, duration_min: int, max_elev: float = 45.0) -> PassEvent:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    aos = base + timedelta(minutes=start_offset_min)
    los = aos + timedelta(minutes=duration_min)
    return PassEvent(
        aos_utc=aos,
        los_utc=los,
        max_elevation_utc=aos + timedelta(minutes=duration_min / 2),
        max_elevation_deg=max_elev,
        duration_seconds=duration_min * 60,
    )


def _mk_request(request_id: str, priority: str = "MEDIUM") -> CommunicationRequest:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return CommunicationRequest(
        request_id=request_id,
        norad_id=5,
        priority=priority,
        earliest_start_utc=base,
        latest_end_utc=base + timedelta(hours=6),
    )


def test_score_increases_with_priority():
    p = _mk_pass(0, 10)
    low = _score("LOW", p)
    high = _score("HIGH", p)
    assert high > low


def test_score_increases_with_elevation():
    low_elev = _mk_pass(0, 10, max_elev=10.0)
    high_elev = _mk_pass(0, 10, max_elev=80.0)
    assert _score("MEDIUM", high_elev) > _score("MEDIUM", low_elev)


def test_non_overlapping_opportunities_all_selected():
    p1 = _mk_pass(0, 10)
    p2 = _mk_pass(30, 10)
    p3 = _mk_pass(60, 10)
    opps = [
        Opportunity(_mk_request("A"), p1, _score("MEDIUM", p1), p1.aos_utc, p1.los_utc),
        Opportunity(_mk_request("B"), p2, _score("MEDIUM", p2), p2.aos_utc, p2.los_utc),
        Opportunity(_mk_request("C"), p3, _score("MEDIUM", p3), p3.aos_utc, p3.los_utc),
    ]
    selected = _weighted_interval_schedule(opps)
    assert len(selected) == 3


def test_overlapping_opportunities_higher_score_wins():
    # Two overlapping passes; the CRITICAL-priority one should win even
    # though it starts slightly later.
    p_low = _mk_pass(0, 20, max_elev=20.0)
    p_high = _mk_pass(5, 20, max_elev=20.0)  # overlaps with p_low
    opps = [
        Opportunity(_mk_request("LOWREQ", "LOW"), p_low, _score("LOW", p_low), p_low.aos_utc, p_low.los_utc),
        Opportunity(
            _mk_request("CRITREQ", "CRITICAL"), p_high, _score("CRITICAL", p_high), p_high.aos_utc, p_high.los_utc
        ),
    ]
    selected = _weighted_interval_schedule(opps)
    assert len(selected) == 1
    assert selected[0].request.request_id == "CRITREQ"


def test_weighted_interval_schedule_maximizes_total_score():
    # Classic 3-interval case: one long low-value interval overlaps two
    # short high-value intervals that don't overlap each other.
    long_low = _mk_pass(0, 60, max_elev=5.0)  # overlaps both short ones
    short1 = _mk_pass(0, 20, max_elev=89.0)
    short2 = _mk_pass(35, 20, max_elev=89.0)

    opps = [
        Opportunity(_mk_request("LONG", "LOW"), long_low, _score("LOW", long_low), long_low.aos_utc, long_low.los_utc),
        Opportunity(_mk_request("S1", "HIGH"), short1, _score("HIGH", short1), short1.aos_utc, short1.los_utc),
        Opportunity(_mk_request("S2", "HIGH"), short2, _score("HIGH", short2), short2.aos_utc, short2.los_utc),
    ]
    selected_ids = {o.request.request_id for o in _weighted_interval_schedule(opps)}
    # The two short, high-priority, high-elevation passes together should
    # outscore the single long low-priority pass.
    assert selected_ids == {"S1", "S2"}


def test_empty_opportunities_returns_empty():
    assert _weighted_interval_schedule([]) == []
