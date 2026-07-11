from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.core.constants import DEFAULT_MIN_CONTACT_SECONDS
from app.models.schemas import PassPredictionRequest, PassPredictionResponse
from app.services.pass_predictor import predict_passes, PassPredictionError
from app.services.tle_provider import get_catalogue

router = APIRouter(tags=["passes"])


@router.post("/passes/predict", response_model=PassPredictionResponse)
def predict(payload: PassPredictionRequest):
    catalogue = get_catalogue()
    tle = catalogue.get(payload.norad_id)
    if tle is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No orbital elements available for NORAD ID {payload.norad_id} in the "
                f"current data source ({catalogue.mode})."
            ),
        )

    try:
        passes = predict_passes(
            tle=tle,
            latitude_deg=payload.ground_station.latitude_deg,
            longitude_deg=payload.ground_station.longitude_deg,
            altitude_m=payload.ground_station.altitude_m,
            min_elevation_deg=payload.ground_station.min_elevation_deg,
            start_time_utc=payload.start_time_utc,
            duration_hours=payload.duration_hours,
            min_contact_seconds=DEFAULT_MIN_CONTACT_SECONDS,
        )
    except PassPredictionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PassPredictionResponse(
        norad_id=payload.norad_id,
        satellite_name=tle.name,
        ground_station=payload.ground_station,
        data_mode=catalogue.mode,  # type: ignore[arg-type]
        window_start_utc=payload.start_time_utc,
        window_end_utc=payload.start_time_utc + timedelta(hours=payload.duration_hours),
        passes=passes,
        pass_count=len(passes),
    )
