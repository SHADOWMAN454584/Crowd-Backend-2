"""Google Maps API integration for real-time crowd data."""

from __future__ import annotations

from typing import Any

try:
    import googlemaps
except ImportError:
    googlemaps = None

try:
    from app.core.config import settings
except Exception:
    settings = None


def _get_maps_client() -> Any:
    """Get or create Google Maps client."""
    if googlemaps is None:
        return None

    api_key = getattr(settings, "google_maps_api_key", None) if settings else None
    if not api_key:
        return None

    try:
        return googlemaps.Client(key=api_key)
    except Exception:
        return None


def get_place_details(place_id: str) -> dict[str, Any]:
    """Get place details from Google Maps Places API."""
    client = _get_maps_client()
    if not client:
        return {
            "status": "unavailable",
            "message": "Google Maps API not configured",
        }

    try:
        result = client.place(place_id, fields=["name", "rating", "user_ratings_total", "geometry"])
        if result.get("status") == "OK":
            place = result.get("result", {})
            return {
                "status": "success",
                "name": place.get("name"),
                "rating": place.get("rating"),
                "userRatingsTotal": place.get("user_ratings_total"),
                "location": place.get("geometry", {}).get("location", {}),
            }
        return {
            "status": "error",
            "message": f"API returned status: {result.get('status')}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def get_nearby_places(latitude: float, longitude: float, radius: int = 1000, place_type: str | None = None) -> dict[str, Any]:
    """Get nearby places from Google Maps Places API."""
    client = _get_maps_client()
    if not client:
        return {
            "status": "unavailable",
            "message": "Google Maps API not configured",
            "places": [],
        }

    try:
        result = client.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            type=place_type,
        )

        if result.get("status") in ["OK", "ZERO_RESULTS"]:
            places = result.get("results", [])
            return {
                "status": "success",
                "places": [
                    {
                        "placeId": place.get("place_id"),
                        "name": place.get("name"),
                        "location": place.get("geometry", {}).get("location", {}),
                        "rating": place.get("rating"),
                        "userRatingsTotal": place.get("user_ratings_total"),
                        "types": place.get("types", []),
                    }
                    for place in places
                ],
            }
        return {
            "status": "error",
            "message": f"API returned status: {result.get('status')}",
            "places": [],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "places": [],
        }


def get_distance_matrix(origins: list[tuple[float, float]], destinations: list[tuple[float, float]]) -> dict[str, Any]:
    """Get distance and duration matrix between origins and destinations."""
    client = _get_maps_client()
    if not client:
        return {
            "status": "unavailable",
            "message": "Google Maps API not configured",
        }

    try:
        result = client.distance_matrix(
            origins=origins,
            destinations=destinations,
            mode="driving",
            departure_time="now",
            traffic_model="best_guess",
        )

        if result.get("status") == "OK":
            return {
                "status": "success",
                "rows": result.get("rows", []),
                "originAddresses": result.get("origin_addresses", []),
                "destinationAddresses": result.get("destination_addresses", []),
            }
        return {
            "status": "error",
            "message": f"API returned status: {result.get('status')}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def get_directions(origin: tuple[float, float], destination: tuple[float, float], mode: str = "driving") -> dict[str, Any]:
    """Get directions between origin and destination with traffic data."""
    client = _get_maps_client()
    if not client:
        return {
            "status": "unavailable",
            "message": "Google Maps API not configured",
        }

    try:
        result = client.directions(
            origin=origin,
            destination=destination,
            mode=mode,
            departure_time="now",
            traffic_model="best_guess",
            alternatives=True,
        )

        if result and len(result) > 0:
            routes = []
            for route in result:
                leg = route.get("legs", [{}])[0]
                routes.append({
                    "summary": route.get("summary"),
                    "distance": leg.get("distance", {}).get("value", 0),
                    "duration": leg.get("duration", {}).get("value", 0),
                    "durationInTraffic": leg.get("duration_in_traffic", {}).get("value", 0) if "duration_in_traffic" in leg else None,
                    "polyline": route.get("overview_polyline", {}).get("points", ""),
                })

            return {
                "status": "success",
                "routes": routes,
            }
        return {
            "status": "error",
            "message": "No routes found",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def estimate_crowd_from_traffic(location_id: str, latitude: float, longitude: float) -> dict[str, Any]:
    """
    Estimate crowd levels based on nearby traffic and place popularity.
    This uses Google Maps data to infer crowd density.
    """
    client = _get_maps_client()
    if not client:
        return {
            "locationId": location_id,
            "crowdEstimate": None,
            "source": "unavailable",
        }

    try:
        # Get nearby popular places
        nearby_result = get_nearby_places(latitude, longitude, radius=500)

        if nearby_result.get("status") != "success":
            return {
                "locationId": location_id,
                "crowdEstimate": None,
                "source": "error",
            }

        places = nearby_result.get("places", [])

        # Calculate crowd estimate based on number of places and their ratings
        total_ratings = sum(place.get("userRatingsTotal", 0) for place in places)
        avg_rating = sum(place.get("rating", 0) for place in places) / max(len(places), 1)

        # Normalize to density scale (0-100)
        crowd_density = min(100.0, (len(places) * 2) + (total_ratings / 100) + (avg_rating * 5))

        return {
            "locationId": location_id,
            "crowdEstimate": round(crowd_density, 2),
            "nearbyPlacesCount": len(places),
            "source": "google_maps",
        }
    except Exception as e:
        return {
            "locationId": location_id,
            "crowdEstimate": None,
            "source": "error",
            "error": str(e),
        }
