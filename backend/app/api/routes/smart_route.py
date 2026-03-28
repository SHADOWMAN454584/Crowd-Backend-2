"""Smart-route endpoints for nearby crowd-aware alternatives."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.smart_route import SmartRouteNearbyRequest, SmartRouteNearbyResponse
from app.services.smart_route_service import get_smart_route_nearby

router = APIRouter()


@router.post("/nearby", response_model=SmartRouteNearbyResponse)
async def smart_route_nearby(payload: SmartRouteNearbyRequest) -> SmartRouteNearbyResponse:
    response = await get_smart_route_nearby(
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_km=payload.radius_km,
    )
    return SmartRouteNearbyResponse(**response)
