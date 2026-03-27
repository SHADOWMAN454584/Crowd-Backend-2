"""
/realtime routes
─────────────────────────────────────────────────────────────────────
GET  /realtime/status   → Maps integration status
GET  /realtime/collect  → Trigger live data collection from Google Maps
GET  /realtime/cached   → Return last collected realtime data
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

from models.schemas import (
    RealtimeStatus,
    RealtimeCollectResponse,
    RealtimeDataPoint,
)
from services.maps_service import maps_service
from services.prediction_service import prediction_service
from config import LOCATIONS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["Realtime"])


def _blend_density(ml_density: float, maps_score: float) -> float:
    """70% ML + 30% Maps activity for final density."""
    if maps_score > 0:
        return round(0.70 * ml_density + 0.30 * maps_score, 2)
    return round(ml_density, 2)


@router.get("/status", response_model=RealtimeStatus)
async def get_realtime_status():
    """
    Returns whether Google Maps is connected and operational.
    Called every 30 seconds by the Flutter app to show the API status badge.
    """
    if maps_service is None:
        return RealtimeStatus(
            maps_enabled=False,
            maps_api_key_set=False,
            last_collection=None,
            locations_covered=0,
            traffic_data_age_seconds=None,
            status_message="Maps service not initialised.",
        )

    status = maps_service.get_status()
    return RealtimeStatus(**status)


@router.get("/collect", response_model=RealtimeCollectResponse)
async def collect_realtime():
    """
    Actively queries Google Maps Places API for each location and
    stores the results in the maps service cache.

    If Maps is unavailable, falls back to current ML predictions so
    the Flutter app always gets a valid response.
    """
    now = datetime.utcnow()

    if maps_service and maps_service.enabled:
        try:
            raw = maps_service.collect_realtime_data(LOCATIONS)

            # Blend Maps activity with ML predictions
            data_points = []
            for item in raw:
                loc = next((l for l in LOCATIONS if l["id"] == item["location_id"]), None)
                if not loc:
                    continue

                hour = now.hour
                ml_density, _ = prediction_service.predict(
                    location_id=loc["id"],
                    location_type=loc["type"],
                    hour=hour,
                )
                maps_score = item.get("maps_activity_score", 0)
                final_density = _blend_density(ml_density, maps_score)

                data_points.append(
                    RealtimeDataPoint(
                        location_id=loc["id"],
                        location_name=loc["name"],
                        latitude=loc["lat"],
                        longitude=loc["lng"],
                        crowd_density=final_density,
                        crowd_count=prediction_service.density_to_count(final_density),
                        status=prediction_service.density_to_status(final_density),
                        traffic_level=item.get("traffic_level"),
                        nearby_places_count=None,
                        source="google_maps+model",
                        collected_at=now,
                    )
                )

            return RealtimeCollectResponse(
                success=True,
                data=data_points,
                collected_at=now,
                source="google_maps",
            )

        except Exception as e:
            logger.error(f"Real-time collection failed: {e}")
            # Fall through to ML fallback

    # ── ML-only fallback ───────────────────────────────────────────────────────
    hour = now.hour
    data_points = []
    for loc in LOCATIONS:
        density, _ = prediction_service.predict(
            location_id=loc["id"],
            location_type=loc["type"],
            hour=hour,
        )
        data_points.append(
            RealtimeDataPoint(
                location_id=loc["id"],
                location_name=loc["name"],
                latitude=loc["lat"],
                longitude=loc["lng"],
                crowd_density=round(density, 2),
                crowd_count=prediction_service.density_to_count(density),
                status=prediction_service.density_to_status(density),
                traffic_level=None,
                nearby_places_count=None,
                source="model",
                collected_at=now,
            )
        )

    return RealtimeCollectResponse(
        success=True,
        data=data_points,
        collected_at=now,
        source="synthetic",
    )


@router.get("/cached", response_model=RealtimeCollectResponse)
async def get_cached_realtime():
    """
    Returns the last successfully collected realtime data.
    If no cache exists, falls back to ML predictions (same as /collect).
    """
    now = datetime.utcnow()

    if maps_service and maps_service.enabled:
        cached = maps_service.get_cached_data()
        if cached:
            data_points = []
            for item in cached:
                loc = next((l for l in LOCATIONS if l["id"] == item["location_id"]), None)
                if not loc:
                    continue

                hour = (item.get("collected_at") or now).hour if isinstance(
                    item.get("collected_at"), datetime
                ) else now.hour

                ml_density, _ = prediction_service.predict(
                    location_id=loc["id"],
                    location_type=loc["type"],
                    hour=hour,
                )
                maps_score = item.get("maps_activity_score", 0)
                final_density = _blend_density(ml_density, maps_score)

                data_points.append(
                    RealtimeDataPoint(
                        location_id=loc["id"],
                        location_name=loc["name"],
                        latitude=loc["lat"],
                        longitude=loc["lng"],
                        crowd_density=final_density,
                        crowd_count=prediction_service.density_to_count(final_density),
                        status=prediction_service.density_to_status(final_density),
                        traffic_level=None,
                        nearby_places_count=None,
                        source="cached_maps+model",
                        collected_at=item.get("collected_at", now),
                    )
                )

            return RealtimeCollectResponse(
                success=True,
                data=data_points,
                collected_at=now,
                source="cached",
            )

    # No cache → trigger fresh ML predictions
    return await collect_realtime()
