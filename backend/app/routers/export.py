from fastapi import APIRouter, Response

from app.models.schemas import ScheduleResult
from app.services.export_service import export_schedule_csv, export_schedule_json

router = APIRouter(tags=["export"])


@router.post("/export/schedule")
def export_schedule(payload: ScheduleResult, format: str = "json"):
    if format == "csv":
        content = export_schedule_csv(payload)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=orbitops_schedule.csv"},
        )
    content = export_schedule_json(payload)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=orbitops_schedule.json"},
    )
