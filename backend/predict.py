"""
/predict routes
─────────────────────────────────────────────────────────────────────
POST /predict/bulk  →  crowd density for all (or selected) locations
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
import logging

from models.schemas import BulkPredictRequest, BulkPredictResponse, CrowdPrediction
from services.prediction_service import prediction_service
from services.maps_service import maps_service
from config import LOCATIONS, LOCATION_MAP

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("/bulk", response_model=BulkPredictResponse)
async def bulk_predict(body: BulkPredictRequest):
    """
    Returns crowd density predictions for all (or specified) locations.

    Called by Flutter app every 30 seconds (×2: current hour + next hour).

    • If Google Maps is active, blends ML prediction with Maps activity score.
    • Otherwise, serves pure ML predictions.
    """
    now = datetime.utcnow()
    hour = body.hour
    day_of_week = body.day_of_week if body.day_of_week is not None else now.weekday()
    is_holiday = body.is_holiday or False

    # Determine which locations to predict
    if body.location_ids:
        locations = [LOCATION_MAP[lid] for lid in body.location_ids if lid in LOCATION_MAP]
        if not locations:
            raise HTTPException(status_code=400, detail="No valid location IDs provided.")
    else:
        locations = LOCATIONS

    # Fetch Maps activity scores if available
    maps_activity: dict = {}
    maps_enabled = maps_service is not None and maps_service.enabled
    if maps_enabled:
        try:
            cached = maps_service.get_cached_data()
            maps_activity = {d["location_id"]: d.get("maps_activity_score", 0) for d in cached}
        except Exception as e:
            logger.warning(f"Could not read maps cache: {e}")

    predictions = []
    for loc in locations:
        density_ml, confidence = prediction_service.predict(
            location_id=loc["id"],
            location_type=loc["type"],
            hour=hour,
            day_of_week=day_of_week,
            is_holiday=is_holiday,
        )

        # Blend Maps activity (weighted 30% Maps / 70% ML)
        if loc["id"] in maps_activity and maps_activity[loc["id"]] > 0:
            maps_score = maps_activity[loc["id"]]
            density = 0.70 * density_ml + 0.30 * maps_score
            source = "realtime+model"
            confidence = min(0.95, confidence + 0.10)
        else:
            density = density_ml
            source = "model"

        # Next-hour prediction (requested via second bulk call but we precompute)
        next_h = (hour + 1) % 24
        density_next, _ = prediction_service.predict(
            location_id=loc["id"],
            location_type=loc["type"],
            hour=next_h,
            day_of_week=day_of_week,
            is_holiday=is_holiday,
        )

        predictions.append(
            CrowdPrediction(
                location_id=loc["id"],
                location_name=loc["name"],
                latitude=loc["lat"],
                longitude=loc["lng"],
                crowd_count=prediction_service.density_to_count(density),
                crowd_density=round(density, 2),
                status=prediction_service.density_to_status(density),
                predicted_next_hour=round(density_next, 2),
                timestamp=now,
                confidence=round(confidence, 3),
                source=source,
            )
        )

    return BulkPredictResponse(
        predictions=predictions,
        model_version=prediction_service.model_version,
        generated_at=now,
        maps_integrated=maps_enabled,
    )
