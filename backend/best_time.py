"""
/best-time route
─────────────────────────────────────────────────────────────────────
GET /best-time?from=metro_a&to=mall_1

Returns 24-hour crowd forecast for both the origin and destination,
the recommended optimal departure hour, and an AI-generated explanation.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
import logging

from models.schemas import BestTimeResponse, HourSlot
from services.prediction_service import prediction_service
from services.ai_service import ai_service
from services.maps_service import maps_service
from config import LOCATION_MAP

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/best-time", tags=["Best Time"])


def _hour_label(h: int) -> str:
    if h == 0:
        return "12 AM"
    elif h < 12:
        return f"{h} AM"
    elif h == 12:
        return "12 PM"
    else:
        return f"{h-12} PM"


@router.get("", response_model=BestTimeResponse)
async def get_best_time(
    from_location: str = Query(..., alias="from", description="Origin location ID"),
    to_location: str = Query(..., alias="to", description="Destination location ID"),
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    is_holiday: bool = Query(False),
):
    """
    Returns the optimal travel time for a given route.

    Algorithm:
    1. Predict crowd density for both locations across all 24 hours
    2. Score each hour: combined = 0.4 × from_density + 0.6 × to_density
       (destination weighted more since it determines wait time)
    3. Optionally blend with Google Maps directions duration
    4. Pick hour with lowest combined score
    5. Use OpenAI to write a human-readable recommendation
    """

    if from_location not in LOCATION_MAP:
        raise HTTPException(status_code=404, detail=f"Location '{from_location}' not found.")
    if to_location not in LOCATION_MAP:
        raise HTTPException(status_code=404, detail=f"Location '{to_location}' not found.")

    from_loc = LOCATION_MAP[from_location]
    to_loc = LOCATION_MAP[to_location]

    now = datetime.utcnow()
    dow = day_of_week if day_of_week is not None else now.weekday()

    # ── 24-hour predictions ────────────────────────────────────────────────────
    from_24h = prediction_service.predict_24h(from_location, from_loc["type"], dow, is_holiday)
    to_24h = prediction_service.predict_24h(to_location, to_loc["type"], dow, is_holiday)

    # ── Score each hour ────────────────────────────────────────────────────────
    combined_scores = []
    for (h, from_d), (_, to_d) in zip(from_24h, to_24h):
        score = 0.4 * from_d + 0.6 * to_d
        combined_scores.append((h, score, from_d, to_d))

    # Optional: adjust for travel time from Google Maps
    route_info = {}
    if maps_service and maps_service.enabled:
        try:
            route_info = maps_service.get_directions(
                from_loc["lat"], from_loc["lng"],
                to_loc["lat"], to_loc["lng"],
            )
        except Exception as e:
            logger.warning(f"Maps directions failed: {e}")

    # ── Find best hour (lowest combined score, between 5 AM and 11 PM) ─────────
    daytime_scores = [s for s in combined_scores if 5 <= s[0] <= 23]
    best = min(daytime_scores, key=lambda x: x[1])
    best_hour, _, best_from_d, best_to_d = best
    best_density = 0.4 * best_from_d + 0.6 * best_to_d

    # ── Build hourly forecast slots ───────────────────────────────────────────
    hourly_forecast = [
        HourSlot(
            hour=h,
            label=_hour_label(h),
            density_from=round(from_d, 1),
            density_to=round(to_d, 1),
            avg_density=round((from_d + to_d) / 2, 1),
            status=prediction_service.density_to_status((from_d + to_d) / 2),
        )
        for h, _, from_d, to_d in combined_scores
    ]

    # ── AI Recommendation ─────────────────────────────────────────────────────
    ai_text = ""
    if ai_service and ai_service.enabled:
        try:
            ai_text = await ai_service.get_best_time_recommendation(
                from_location=from_loc["name"],
                to_location=to_loc["name"],
                best_hour=best_hour,
                expected_density=best_density,
                status=prediction_service.density_to_status(best_density),
                hourly_densities=[(h, d) for h, _, d, _ in combined_scores],
            )
        except Exception as e:
            logger.error(f"AI recommendation failed: {e}")

    if not ai_text:
        ai_text = (
            f"Best time to travel from {from_loc['name']} to {to_loc['name']} "
            f"is around {_hour_label(best_hour)} with ~{best_density:.0f}% crowd density. "
        )
        if route_info.get("duration_minutes"):
            ai_text += f"Estimated travel time: {route_info['duration_minutes']:.0f} minutes."

    return BestTimeResponse(
        from_location=from_loc["name"],
        to_location=to_loc["name"],
        best_hour=best_hour,
        best_hour_label=_hour_label(best_hour),
        expected_density=round(best_density, 2),
        status=prediction_service.density_to_status(best_density),
        hourly_forecast=hourly_forecast,
        ai_recommendation=ai_text,
        generated_at=now,
    )
