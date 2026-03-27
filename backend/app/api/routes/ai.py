from typing import Any

from fastapi import APIRouter

from app.services.openai_service import generate_insights, generate_route_advice
from app.services.prediction_service import get_bulk_predictions

router = APIRouter()


@router.post("/insights")
async def ai_insights(payload: dict[str, Any] | None = None) -> dict:
    request_payload = payload or {}
    crowd_data = request_payload.get("crowdData") or get_bulk_predictions(hour=None)
    summary = await generate_insights(crowd_data=crowd_data)
    return {
        "summary": summary,
        "dataPoints": len(crowd_data),
    }


@router.post("/route-advice")
async def ai_route_advice(payload: dict[str, Any]) -> dict:
    items = payload.get("crowdData", [])
    origin = payload.get("origin")
    destination = payload.get("destination")
    advice = await generate_route_advice(items, origin=origin, destination=destination)
    return advice