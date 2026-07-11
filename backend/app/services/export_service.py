"""Export helpers for schedule results."""
from __future__ import annotations

import csv
import io
import json

from app.models.schemas import ScheduleResult


def export_schedule_json(result: ScheduleResult) -> str:
    return result.model_dump_json(indent=2)


def export_schedule_csv(result: ScheduleResult) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "request_id",
            "norad_id",
            "satellite_name",
            "priority",
            "aos_utc",
            "los_utc",
            "max_elevation_deg",
            "score",
            "reason",
        ]
    )
    for c in result.scheduled:
        writer.writerow(
            [
                c.request_id,
                c.norad_id,
                c.satellite_name or "",
                c.priority,
                c.aos_utc.isoformat(),
                c.los_utc.isoformat(),
                c.max_elevation_deg,
                c.score,
                c.reason,
            ]
        )
    writer.writerow([])
    writer.writerow(["-- rejected --"])
    writer.writerow(["request_id", "norad_id", "reason"])
    for r in result.rejected:
        writer.writerow([r.request_id, r.norad_id, r.reason])
    return buffer.getvalue()
