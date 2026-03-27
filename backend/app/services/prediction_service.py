from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from app.core.constants import DEFAULT_PREDICTION_HOUR, HIGH_DENSITY_THRESHOLD, LOW_DENSITY_THRESHOLD
except Exception:
    DEFAULT_PREDICTION_HOUR = datetime.now().hour
    LOW_DENSITY_THRESHOLD = 35
    HIGH_DENSITY_THRESHOLD = 70

try:
    from app.data.locations import SEEDED_LOCATIONS
except Exception:
    SEEDED_LOCATIONS: list[dict[str, Any]] = []


def _normalize_hour(hour: int | None) -> int:
    if hour is None:
        return int(DEFAULT_PREDICTION_HOUR)
    return int(hour) % 24


def _extract_coordinates(location: dict[str, Any]) -> tuple[float, float]:
    latitude = location.get("latitude", location.get("lat", 0.0))
    longitude = location.get("longitude", location.get("lng", location.get("lon", 0.0)))
    return float(latitude), float(longitude)


def _resolve_density_profile(location: dict[str, Any]) -> dict[str, Any]:
    profile = location.get("baselineDensityProfile") or location.get("baseline_density_profile") or {}
    return profile if isinstance(profile, dict) else {}


def _density_from_hour(location: dict[str, Any], hour: int) -> float:
    profile = _resolve_density_profile(location)
    if hour in profile:
        return float(profile[hour])

    hour_key = str(hour)
    if hour_key in profile:
        return float(profile[hour_key])

    for key, value in profile.items():
        if isinstance(key, str) and "-" in key:
            try:
                start_text, end_text = key.split("-", maxsplit=1)
                start_hour = int(start_text)
                end_hour = int(end_text)
            except ValueError:
                continue

            if start_hour <= end_hour and start_hour <= hour <= end_hour:
                return float(value)
            if start_hour > end_hour and (hour >= start_hour or hour <= end_hour):
                return float(value)

    fallback = location.get("baselineDensity") or location.get("baseline_density") or 25
    return float(fallback)


def _clamp_density(density: float) -> float:
    return max(0.0, min(100.0, round(float(density), 2)))


def _density_to_status(density: float) -> str:
    if density >= float(HIGH_DENSITY_THRESHOLD):
        return "high"
    if density >= float(LOW_DENSITY_THRESHOLD):
        return "medium"
    return "low"


def _density_to_count(density: float) -> int:
    return int(round(float(density) * 5))


def build_crowd_data(location: dict[str, Any], hour: int | None = None, timestamp: datetime | None = None) -> dict[str, Any]:
    target_hour = _normalize_hour(hour)
    latitude, longitude = _extract_coordinates(location)
    density = _clamp_density(_density_from_hour(location, target_hour))
    next_hour_density = _clamp_density(_density_from_hour(location, (target_hour + 1) % 24))
    current_timestamp = (timestamp or datetime.now(timezone.utc)).isoformat()

    return {
        "locationId": str(location.get("id", "")),
        "locationName": location.get("name", "Unknown Location"),
        "latitude": latitude,
        "longitude": longitude,
        "crowdCount": _density_to_count(density),
        "crowdDensity": density,
        "status": _density_to_status(density),
        "timestamp": current_timestamp,
        "predictedNextHour": next_hour_density,
    }


def get_bulk_predictions(hour: int | None = None) -> list[dict[str, Any]]:
    target_hour = _normalize_hour(hour)
    timestamp = datetime.now(timezone.utc)
    return [build_crowd_data(location, hour=target_hour, timestamp=timestamp) for location in SEEDED_LOCATIONS]