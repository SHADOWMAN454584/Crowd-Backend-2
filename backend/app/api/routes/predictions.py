from fastapi import APIRouter, Query

from app.services.prediction_service import get_bulk_predictions

router = APIRouter()


@router.get("/bulk")
async def get_predictions_bulk(hour: int | None = Query(default=None, ge=0, le=23)) -> dict:
    data = get_bulk_predictions(hour=hour)
    return {
        "hour": hour,
        "data": data,
    }