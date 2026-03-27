"""
Google Maps Service
─────────────────────────────────────────────────────────────────────
Uses the Google Maps Python client to:
  1. Find nearby places to estimate footfall/activity levels
  2. Get route/directions info for travel time estimates
  3. Get traffic conditions between locations

Requires: GOOGLE_MAPS_API_KEY in .env
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── Optional import (graceful degradation if key not set) ──────────────────────
try:
    import googlemaps
    GMAPS_AVAILABLE = True
except ImportError:
    GMAPS_AVAILABLE = False
    logger.warning("googlemaps package not found. Maps features disabled.")


# How much nearby activity → crowd density contribution (heuristic)
ACTIVITY_DENSITY_WEIGHT = {
    "restaurant": 8,
    "cafe": 6,
    "bar": 7,
    "movie_theater": 12,
    "shopping_mall": 15,
    "subway_station": 20,
    "train_station": 20,
    "bus_station": 10,
    "park": 5,
    "stadium": 25,
    "hospital": 8,
    "school": 10,
    "bank": 4,
    "atm": 2,
    "store": 5,
}

# Traffic level description → density modifier
TRAFFIC_DENSITY_MAP = {
    "1": 10,   # Free flow
    "2": 30,   # Light traffic
    "3": 55,   # Moderate
    "4": 75,   # Heavy
    "5": 90,   # Very heavy / gridlock
}


class MapsService:
    """Wraps Google Maps API calls with caching and graceful fallback."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client: Optional[object] = None
        self._cache: Dict[str, Tuple[dict, float]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_collection: Optional[datetime] = None
        self._cached_data: List[dict] = []
        self.enabled = False

        if api_key and GMAPS_AVAILABLE:
            try:
                self.client = googlemaps.Client(key=api_key)
                self.enabled = True
                logger.info("Google Maps client initialized.")
            except Exception as e:
                logger.error(f"Failed to init Google Maps client: {e}")

    # ── Cache Helpers ─────────────────────────────────────────────────────────

    def _cache_get(self, key: str) -> Optional[dict]:
        if key in self._cache:
            data, ts = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                return data
            del self._cache[key]
        return None

    def _cache_set(self, key: str, data: dict):
        self._cache[key] = (data, time.time())

    # ── Status ────────────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        age = None
        if self._last_collection:
            age = int((datetime.utcnow() - self._last_collection).total_seconds())

        return {
            "maps_enabled": self.enabled,
            "maps_api_key_set": bool(self.api_key),
            "last_collection": self._last_collection,
            "locations_covered": len(self._cached_data),
            "traffic_data_age_seconds": age,
            "status_message": (
                "Google Maps integration active and collecting data."
                if self.enabled
                else "Maps API key not configured — using ML predictions only."
            ),
        }

    # ── Nearby Places ─────────────────────────────────────────────────────────

    def get_nearby_activity(self, lat: float, lng: float, radius: int = 500) -> float:
        """
        Queries nearby places and returns an estimated crowd contribution (0-100).
        Uses a weighted sum of place types found.
        """
        if not self.enabled:
            return 0.0

        cache_key = f"nearby_{lat:.4f}_{lng:.4f}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached["score"]

        try:
            result = self.client.places_nearby(
                location=(lat, lng),
                radius=radius,
                rank_by="prominence",
            )
            places = result.get("results", [])
            score = 0.0
            for place in places[:20]:  # top 20 results
                for ptype in place.get("types", []):
                    weight = ACTIVITY_DENSITY_WEIGHT.get(ptype, 0)
                    # Rating boosts score slightly
                    rating_boost = place.get("rating", 3.0) / 5.0
                    score += weight * (0.7 + 0.3 * rating_boost)

            # Normalize to 0-100
            normalized = min(100.0, score / 3.0)
            self._cache_set(cache_key, {"score": normalized})
            return normalized

        except Exception as e:
            logger.error(f"places_nearby failed: {e}")
            return 0.0

    # ── Directions / Travel Time ───────────────────────────────────────────────

    def get_directions(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        departure_hour: int = 8,
    ) -> dict:
        """
        Gets route info between two lat/lng points.
        Returns duration_minutes, distance_km, and a traffic_level string.
        """
        if not self.enabled:
            return {"duration_minutes": None, "distance_km": None, "traffic_level": None}

        cache_key = f"dir_{origin_lat:.4f}_{origin_lng:.4f}_{dest_lat:.4f}_{dest_lng:.4f}_{departure_hour}"
        cached = self._cache_get(cache_key)
        if cached:
            return cached

        try:
            result = self.client.directions(
                origin=(origin_lat, origin_lng),
                destination=(dest_lat, dest_lng),
                mode="transit",
                alternatives=False,
            )

            if not result:
                return {"duration_minutes": None, "distance_km": None, "traffic_level": None}

            leg = result[0]["legs"][0]
            duration_sec = leg["duration"]["value"]
            distance_m = leg["distance"]["value"]

            data = {
                "duration_minutes": round(duration_sec / 60, 1),
                "distance_km": round(distance_m / 1000, 2),
                "traffic_level": "moderate",  # transit doesn't return traffic level
            }
            self._cache_set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"directions failed: {e}")
            return {"duration_minutes": None, "distance_km": None, "traffic_level": None}

    # ── Collect Live Data for All Locations ──────────────────────────────────

    def collect_realtime_data(self, locations: List[dict]) -> List[dict]:
        """
        For each location: query nearby activity and blend with ML signal.
        Returns list of realtime data points.
        """
        results = []
        for loc in locations:
            activity_score = self.get_nearby_activity(loc["lat"], loc["lng"])
            results.append({
                "location_id": loc["id"],
                "location_name": loc["name"],
                "latitude": loc["lat"],
                "longitude": loc["lng"],
                "maps_activity_score": activity_score,
                "collected_at": datetime.utcnow(),
            })

        self._last_collection = datetime.utcnow()
        self._cached_data = results
        return results

    def get_cached_data(self) -> List[dict]:
        return self._cached_data

    # ── Place Details ─────────────────────────────────────────────────────────

    def search_place(self, name: str, lat: float, lng: float) -> Optional[str]:
        """Returns place_id for a named location near coordinates."""
        if not self.enabled:
            return None
        try:
            result = self.client.find_place(
                input=name,
                input_type="textquery",
                fields=["place_id", "name"],
                location_bias=f"circle:500@{lat},{lng}",
            )
            candidates = result.get("candidates", [])
            if candidates:
                return candidates[0]["place_id"]
        except Exception as e:
            logger.error(f"find_place failed: {e}")
        return None


# ── Module-level singleton (initialised in main.py after settings load) ───────
maps_service: Optional[MapsService] = None


def init_maps_service(api_key: str) -> MapsService:
    global maps_service
    maps_service = MapsService(api_key=api_key)
    return maps_service
