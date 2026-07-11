from fastapi import APIRouter

from app.models.schemas import ScheduleGenerationRequest, ScheduleResult
from app.services.scheduler import generate_schedule
from app.services.tle_provider import get_catalogue

router = APIRouter(tags=["schedule"])


@router.post("/schedule/generate", response_model=ScheduleResult)
def generate(payload: ScheduleGenerationRequest):
    catalogue = get_catalogue()
    return generate_schedule(catalogue, payload.ground_station, payload.requests)
