"""Google Maps API routes."""

from typing import Any

from fastapi import APIRouter, Query

from app.services.google_maps_service import (
    estimate_crowd_from_traffic,
    get_directions,
    get_distance_matrix,
    get_nearby_places,
    get_place_details,
)

router = APIRouter()


@router.get("/place/{place_id}")
async def maps_place_details(place_id: str) -> dict[str, Any]:
    """Get details for a specific place from Google Maps."""
    return get_place_details(place_id)


@router.get("/nearby")
async def maps_nearby_places(
    latitude: float = Query(..., description="Latitude of the center point"),
    longitude: float = Query(..., description="Longitude of the center point"),
    radius: int = Query(default=1000, ge=100, le=50000, description="Search radius in meters"),
    place_type: str | None = Query(default=None, description="Type of place to search for"),
) -> dict[str, Any]:
    """Get nearby places from Google Maps."""
    return get_nearby_places(latitude, longitude, radius, place_type)


@router.post("/distance-matrix")
async def maps_distance_matrix(payload: dict[str, Any]) -> dict[str, Any]:
    """Get distance and travel time matrix between multiple origins and destinations."""
    origins = payload.get("origins", [])
    destinations = payload.get("destinations", [])

    if not origins or not destinations:
        return {
            "status": "error",
            "message": "Both origins and destinations are required",
        }

    # Convert to tuples if needed
    origin_tuples = [(o["lat"], o["lng"]) if isinstance(o, dict) else tuple(o) for o in origins]
    dest_tuples = [(d["lat"], d["lng"]) if isinstance(d, dict) else tuple(d) for d in destinations]

    return get_distance_matrix(origin_tuples, dest_tuples)


@router.post("/directions")
async def maps_directions(payload: dict[str, Any]) -> dict[str, Any]:
    """Get directions between origin and destination with traffic data."""
    origin = payload.get("origin")
    destination = payload.get("destination")
    mode = payload.get("mode", "driving")

    if not origin or not destination:
        return {
            "status": "error",
            "message": "Both origin and destination are required",
        }

    # Convert to tuple if needed
    origin_tuple = (origin["lat"], origin["lng"]) if isinstance(origin, dict) else tuple(origin)
    dest_tuple = (destination["lat"], destination["lng"]) if isinstance(destination, dict) else tuple(destination)

    return get_directions(origin_tuple, dest_tuple, mode)


@router.get("/estimate-crowd/{location_id}")
async def maps_estimate_crowd(
    location_id: str,
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
) -> dict[str, Any]:
    """Estimate crowd levels based on Google Maps data (traffic, place popularity)."""
    return estimate_crowd_from_traffic(location_id, latitude, longitude)
