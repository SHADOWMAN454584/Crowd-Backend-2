"""Seeded locations for crowd prediction and realtime mock data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocationSeed:
    """Simple location seed structure for service consumption."""

    id: str
    name: str
    latitude: float
    longitude: float
    category: str
    tags: list[str]
    baseline_density_by_hour: dict[int, float]


def _build_hourly_profile(
    overnight: float,
    morning: float,
    midday: float,
    afternoon: float,
    evening: float,
    late_evening: float,
) -> dict[int, float]:
    profile: dict[int, float] = {}
    for hour in range(0, 6):
        profile[hour] = overnight
    for hour in range(6, 10):
        profile[hour] = morning
    for hour in range(10, 14):
        profile[hour] = midday
    for hour in range(14, 18):
        profile[hour] = afternoon
    for hour in range(18, 22):
        profile[hour] = evening
    for hour in range(22, 24):
        profile[hour] = late_evening
    return profile


LOCATIONS: list[LocationSeed] = [
    LocationSeed(
        id="loc-central-station",
        name="Central Railway Station",
        latitude=23.8103,
        longitude=90.4125,
        category="transport",
        tags=["commuter", "transit", "station"],
        baseline_density_by_hour=_build_hourly_profile(18.0, 68.0, 55.0, 62.0, 74.0, 30.0),
    ),
    LocationSeed(
        id="loc-gulshan-circle",
        name="Gulshan Circle",
        latitude=23.7925,
        longitude=90.4078,
        category="commercial",
        tags=["business", "shopping", "traffic"],
        baseline_density_by_hour=_build_hourly_profile(12.0, 42.0, 66.0, 71.0, 58.0, 24.0),
    ),
    LocationSeed(
        id="loc-dhanmondi-lake",
        name="Dhanmondi Lake Park",
        latitude=23.7461,
        longitude=90.3742,
        category="recreation",
        tags=["park", "walking", "family"],
        baseline_density_by_hour=_build_hourly_profile(8.0, 24.0, 39.0, 47.0, 69.0, 26.0),
    ),
    LocationSeed(
        id="loc-new-market",
        name="New Market",
        latitude=23.7349,
        longitude=90.3854,
        category="market",
        tags=["retail", "shopping", "street-food"],
        baseline_density_by_hour=_build_hourly_profile(10.0, 34.0, 73.0, 78.0, 64.0, 22.0),
    ),
    LocationSeed(
        id="loc-university-campus",
        name="University Campus",
        latitude=23.7288,
        longitude=90.3983,
        category="education",
        tags=["students", "campus", "events"],
        baseline_density_by_hour=_build_hourly_profile(6.0, 58.0, 76.0, 61.0, 37.0, 14.0),
    ),
    LocationSeed(
        id="loc-riverfront-terminal",
        name="Riverfront Launch Terminal",
        latitude=23.7085,
        longitude=90.4073,
        category="transport",
        tags=["ferry", "terminal", "commuter"],
        baseline_density_by_hour=_build_hourly_profile(16.0, 51.0, 48.0, 57.0, 72.0, 34.0),
    ),
    LocationSeed(
        id="loc-city-hospital",
        name="City General Hospital",
        latitude=23.7512,
        longitude=90.3921,
        category="healthcare",
        tags=["hospital", "emergency", "visitors"],
        baseline_density_by_hour=_build_hourly_profile(22.0, 44.0, 52.0, 49.0, 46.0, 28.0),
    ),
]


LOCATION_LOOKUP: dict[str, LocationSeed] = {location.id: location for location in LOCATIONS}


def _location_to_dict(location: LocationSeed) -> dict:
    """Convert LocationSeed to dictionary format."""
    return {
        "id": location.id,
        "name": location.name,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "category": location.category,
        "tags": location.tags,
        "baselineDensityProfile": location.baseline_density_by_hour,
    }


SEEDED_LOCATIONS: list[dict] = [_location_to_dict(location) for location in LOCATIONS]