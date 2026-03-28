"""Models for smart nearby route suggestions."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SmartRouteNearbyRequest(BaseModel):
    """Request payload for nearby smart route suggestions."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=12.0, gt=0, le=100)

    model_config = ConfigDict(populate_by_name=True)


class NearbySmartLocation(BaseModel):
    """Nearby monitored location with predicted crowd signal."""

    location_id: str
    location_name: str
    distance_km: float
    predicted_density: float
    status: str


class SmartRouteSuggestion(BaseModel):
    """Alternative suggestion for a crowded nearby location."""

    original_location_id: str
    original_location_name: str
    original_density: float
    original_distance_km: float
    alternative_location_id: str
    alternative_location_name: str
    alternative_density: float
    alternative_distance_km: float
    savings: float
    fastest_route_minutes: float | None = None
    fastest_route_distance_km: float | None = None
    route_source: str | None = None
    selection_source: str | None = None
    ai_reason: str | None = None


class SmartRouteNearbyResponse(BaseModel):
    """Nearby smart route response payload."""

    radius_km: float
    nearby_locations: list[NearbySmartLocation]
    suggestions: list[SmartRouteSuggestion]
