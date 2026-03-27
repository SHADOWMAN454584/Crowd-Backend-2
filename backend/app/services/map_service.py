from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Any

import httpx

try:
    from app.core.config import settings
except Exception:
    settings = None


def _haversine_km(origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float) -> float:
    earth_radius_km = 6371.0
    dlat = radians(destination_lat - origin_lat)
    dlng = radians(destination_lng - origin_lng)
    lat1 = radians(origin_lat)
    lat2 = radians(destination_lat)

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c


def _fallback_route_metadata(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    distance_km = round(_haversine_km(origin[0], origin[1], destination[0], destination[1]), 2)
    duration_minutes = max(5, int(round(distance_km / 28 * 60)))
    return {
        "provider": "mocked-osm",
        "distanceKm": distance_km,
        "durationMinutes": duration_minutes,
        "geometry": [],
        "isLive": False,
    }


async def get_route_metadata(origin: tuple[float, float], destination: tuple[float, float]) -> dict[str, Any]:
    base_url = getattr(settings, "OSM_ROUTING_URL", "") if settings else ""
    if not base_url:
        return _fallback_route_metadata(origin, destination)

    request_url = f"{base_url.rstrip('/')}/route/v1/driving/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    params = {"overview": "false", "steps": "false"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(request_url, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return _fallback_route_metadata(origin, destination)

    routes = payload.get("routes") or []
    if not routes:
        return _fallback_route_metadata(origin, destination)

    first_route = routes[0]
    return {
        "provider": "osrm",
        "distanceKm": round(float(first_route.get("distance", 0.0)) / 1000, 2),
        "durationMinutes": max(1, int(round(float(first_route.get("duration", 0.0)) / 60))),
        "geometry": first_route.get("geometry", []),
        "isLive": True,
    }