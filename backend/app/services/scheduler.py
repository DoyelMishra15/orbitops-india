"""
Ground-station scheduling engine.

ALGORITHM (fully explainable — no opaque "AI score"):

    1. FEASIBILITY: for every communication request, predict passes of its
       satellite over the ground station, restricted to the request's own
       [earliest_start_utc, latest_end_utc] window and its
       min_elevation_deg mask. Requests with no pass meeting
       min_contact_seconds are rejected immediately with a clear reason.

    2. CANDIDATE SELECTION: among a request's feasible passes, the single
       best pass (highest maximum elevation, a good proxy for link quality)
       is chosen as that request's scheduling opportunity. (Limitation:
       only one opportunity per request is considered — see docs.)

    3. SCORING: each opportunity gets an explainable score:

           score = priority_weight
                   * (1 + max_elevation_deg / 90)     # pass-quality factor
                   * (duration_seconds / 3600)         # contact-length factor

       priority_weight comes from a fixed table (LOW=1, MEDIUM=2, HIGH=3,
       CRITICAL=4). Every term is visible and traceable — nothing here is a
       black-box prediction.

    4. CONFLICT RESOLUTION: a single ground station can only serve one
       contact at a time. Opportunities are resolved with the classical
       *weighted interval scheduling* dynamic-programming algorithm, which
       provably maximises total selected score subject to no two selected
       contacts overlapping. This is the same textbook DP taught in
       algorithms courses (sort by end time; dp[i] = max(dp[i-1],
       score_i + dp[predecessor(i)])) — easy to explain and defend in a
       technical interview, and optimal for the stated objective.

    5. EXPLANATION: every scheduled and rejected request carries a
       human-readable reason string.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.core.constants import PRIORITY_WEIGHT
from app.models.schemas import (
    CommunicationRequest,
    GroundStation,
    PassEvent,
    RejectedRequest,
    ScheduledContact,
    ScheduleResult,
)
from app.services.pass_predictor import predict_passes, PassPredictionError
from app.services.tle_provider import TleCatalogue


@dataclass
class Opportunity:
    request: CommunicationRequest
    pass_event: PassEvent
    score: float
    start: datetime
    end: datetime


def _best_pass_for_request(
    catalogue: TleCatalogue,
    ground_station: GroundStation,
    request: CommunicationRequest,
) -> tuple[Optional[PassEvent], Optional[str]]:
    """Returns (best_pass, rejection_reason). Exactly one of the two is None."""
    tle = catalogue.get(request.norad_id)
    if tle is None:
        return None, f"No orbital elements available for NORAD ID {request.norad_id} in the current data source."

    duration_hours = (request.latest_end_utc - request.earliest_start_utc).total_seconds() / 3600.0
    if duration_hours <= 0:
        return None, "Requested time window has zero or negative length."

    try:
        passes = predict_passes(
            tle=tle,
            latitude_deg=ground_station.latitude_deg,
            longitude_deg=ground_station.longitude_deg,
            altitude_m=ground_station.altitude_m,
            min_elevation_deg=request.min_elevation_deg,
            start_time_utc=request.earliest_start_utc,
            duration_hours=duration_hours,
            min_contact_seconds=request.min_contact_seconds,
        )
    except PassPredictionError as exc:
        return None, f"Propagation error: {exc}"

    if not passes:
        return None, (
            f"No pass above {request.min_elevation_deg}\u00b0 elevation lasting at least "
            f"{int(request.min_contact_seconds)}s was found in the requested window."
        )

    best = max(passes, key=lambda p: p.max_elevation_deg)
    return best, None


def _score(priority: str, pass_event: PassEvent) -> float:
    weight = PRIORITY_WEIGHT.get(priority, 1.0)
    quality_factor = 1.0 + (pass_event.max_elevation_deg / 90.0)
    duration_factor = pass_event.duration_seconds / 3600.0
    return round(weight * quality_factor * duration_factor, 6)


def _weighted_interval_schedule(opportunities: List[Opportunity]) -> List[Opportunity]:
    """Classical weighted interval scheduling DP. Returns the selected subset
    maximising total score with no overlapping intervals."""
    if not opportunities:
        return []

    ordered = sorted(opportunities, key=lambda o: o.end)
    starts = [o.start for o in ordered]
    ends = [o.end for o in ordered]
    n = len(ordered)

    # predecessor(i): last job j (0-indexed, j < i) with ends[j] <= starts[i]
    predecessor: List[int] = []
    for i in range(n):
        # binary search among ends[0..i-1] for the rightmost end <= starts[i]
        lo, hi = 0, i - 1
        p = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ends[mid] <= starts[i]:
                p = mid
                lo = mid + 1
            else:
                hi = mid - 1
        predecessor.append(p)

    dp = [0.0] * (n + 1)
    for i in range(1, n + 1):
        idx = i - 1
        include = ordered[idx].score + (dp[predecessor[idx] + 1] if predecessor[idx] != -1 else 0.0)
        exclude = dp[i - 1]
        dp[i] = max(include, exclude)

    # Backtrack to find the selected set
    selected: List[Opportunity] = []
    i = n
    while i > 0:
        idx = i - 1
        include = ordered[idx].score + (dp[predecessor[idx] + 1] if predecessor[idx] != -1 else 0.0)
        if include >= dp[i - 1]:
            selected.append(ordered[idx])
            i = predecessor[idx] + 1
        else:
            i -= 1

    selected.reverse()
    return selected


def generate_schedule(
    catalogue: TleCatalogue,
    ground_station: GroundStation,
    requests: List[CommunicationRequest],
) -> ScheduleResult:
    opportunities: List[Opportunity] = []
    rejected: List[RejectedRequest] = []

    for req in requests:
        best_pass, reason = _best_pass_for_request(catalogue, ground_station, req)
        if best_pass is None:
            rejected.append(RejectedRequest(request_id=req.request_id, norad_id=req.norad_id, reason=reason or "Infeasible"))
            continue
        opportunities.append(
            Opportunity(
                request=req,
                pass_event=best_pass,
                score=_score(req.priority, best_pass),
                start=best_pass.aos_utc,
                end=best_pass.los_utc,
            )
        )

    selected = _weighted_interval_schedule(opportunities)
    selected_ids = {id(o) for o in selected}

    scheduled: List[ScheduledContact] = []
    for o in selected:
        scheduled.append(
            ScheduledContact(
                request_id=o.request.request_id,
                norad_id=o.request.norad_id,
                satellite_name=o.request.satellite_name,
                priority=o.request.priority,
                aos_utc=o.pass_event.aos_utc,
                los_utc=o.pass_event.los_utc,
                max_elevation_deg=o.pass_event.max_elevation_deg,
                scheduled_start_utc=o.pass_event.aos_utc,
                scheduled_end_utc=o.pass_event.los_utc,
                score=o.score,
                reason=(
                    f"Selected by weighted interval scheduling: priority={o.request.priority}, "
                    f"max_elevation={o.pass_event.max_elevation_deg}\u00b0, "
                    f"duration={int(o.pass_event.duration_seconds)}s, score={o.score}."
                ),
            )
        )

    for o in opportunities:
        if id(o) not in selected_ids:
            rejected.append(
                RejectedRequest(
                    request_id=o.request.request_id,
                    norad_id=o.request.norad_id,
                    reason=(
                        f"A feasible pass existed (score={o.score}) but it overlapped with "
                        "higher-total-value contact(s) selected for the ground station in this window."
                    ),
                )
            )

    scheduled.sort(key=lambda c: c.scheduled_start_utc)

    utilization_seconds = sum((c.scheduled_end_utc - c.scheduled_start_utc).total_seconds() for c in scheduled)

    window_start = min((r.earliest_start_utc for r in requests), default=None)
    window_end = max((r.latest_end_utc for r in requests), default=None)
    total_window_seconds = (
        (window_end - window_start).total_seconds() if window_start and window_end else 0
    )
    utilization_pct = (
        round(100.0 * utilization_seconds / total_window_seconds, 2) if total_window_seconds > 0 else 0.0
    )

    return ScheduleResult(
        ground_station=ground_station,
        scheduled=scheduled,
        rejected=rejected,
        total_requests=len(requests),
        scheduled_count=len(scheduled),
        rejected_count=len(rejected),
        utilization_seconds=round(utilization_seconds, 1),
        window_start_utc=window_start,
        window_end_utc=window_end,
        utilization_pct=utilization_pct,
    )
