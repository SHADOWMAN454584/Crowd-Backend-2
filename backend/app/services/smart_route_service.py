from __future__ import annotations

import json
from math import atan2, cos, radians, sin, sqrt
from typing import Any

try:
    from openai import AsyncOpenAI
except Exception:
    AsyncOpenAI = None

from app.core.config import settings
from app.core.constants import HIGH_DENSITY_THRESHOLD
from app.services.google_maps_service import get_directions
from app.services.prediction_service import get_bulk_predictions

DEFAULT_RADIUS_KM = 12.0
FALLBACK_SPEED_KMH = 28.0
MAX_CANDIDATES_PER_LOCATION = 4


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    rlat1 = radians(lat1)
    rlat2 = radians(lat2)

    a = sin(delta_lat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_km * c


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalized_radius(radius_km: float | None) -> float:
    if radius_km is None:
        return DEFAULT_RADIUS_KM
    return round(max(0.1, float(radius_km)), 2)


def _safe_json_loads(raw_text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw_text)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(raw_text[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _build_route_metrics(
    user_lat: float,
    user_lng: float,
    target_lat: float,
    target_lng: float,
) -> dict[str, Any]:
    directions = get_directions(
        origin=(user_lat, user_lng),
        destination=(target_lat, target_lng),
        mode="driving",
    )

    if directions.get("status") == "success":
        routes = directions.get("routes") or []
        if routes:
            best_route = min(
                routes,
                key=lambda route: _to_float(route.get("durationInTraffic") or route.get("duration"), float("inf")),
            )
            distance_km = round(_to_float(best_route.get("distance")) / 1000, 2)
            duration_minutes = round(
                _to_float(best_route.get("durationInTraffic") or best_route.get("duration")) / 60,
                1,
            )
            return {
                "route_distance_km": max(distance_km, 0.0),
                "route_duration_minutes": max(duration_minutes, 1.0),
                "route_source": "google_maps",
            }

    fallback_distance_km = round(_haversine_km(user_lat, user_lng, target_lat, target_lng), 2)
    fallback_duration_minutes = round(max(1.0, (fallback_distance_km / FALLBACK_SPEED_KMH) * 60), 1)
    return {
        "route_distance_km": fallback_distance_km,
        "route_duration_minutes": fallback_duration_minutes,
        "route_source": "haversine_fallback",
    }


def _heuristic_pick(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        candidates,
        key=lambda item: (
            _to_float(item.get("route_duration_minutes"), float("inf")),
            _to_float(item.get("predicted_density"), float("inf")),
            _to_float(item.get("distance_km"), float("inf")),
        ),
    )


async def _select_fastest_candidate_with_openai(
    user_lat: float,
    user_lng: float,
    original: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> tuple[dict[str, Any], str, str | None]:
    fallback = _heuristic_pick(candidates)
    api_key = settings.openai_api_key
    if not api_key or AsyncOpenAI is None:
        return fallback, "heuristic", None

    model = settings.openai_model or "gpt-4o-mini"
    serialized_candidates = [
        {
            "alternative_location_id": candidate["location_id"],
            "alternative_location_name": candidate["location_name"],
            "alternative_density": candidate["predicted_density"],
            "alternative_distance_km": candidate["distance_km"],
            "route_duration_minutes": candidate["route_duration_minutes"],
            "route_distance_km": candidate["route_distance_km"],
            "route_source": candidate["route_source"],
        }
        for candidate in candidates
    ]

    user_payload = {
        "user": {"latitude": user_lat, "longitude": user_lng},
        "crowded_location": {
            "location_id": original["location_id"],
            "location_name": original["location_name"],
            "density": original["predicted_density"],
            "distance_km": original["distance_km"],
        },
        "candidate_alternatives": serialized_candidates,
        "selection_goal": "Pick the best fastest alternative while also reducing crowd density compared to crowded_location.",
    }

    system_prompt = (
        "You are a routing assistant. Return valid JSON only. "
        "Select one candidate that best balances fastest travel time with lower crowd density. "
        "If multiple candidates are close in travel time, prefer the lower crowd density option."
    )

    schema_prompt = (
        "Return this JSON object exactly with these keys: "
        "alternative_location_id (string), reason (string), confidence (number 0-1)."
    )

    try:
        client = AsyncOpenAI(api_key=api_key)
        completion = await client.chat.completions.create(
            model=model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{schema_prompt}\n\nInput:\n{json.dumps(user_payload)}"},
            ],
        )
    except Exception:
        return fallback, "heuristic", None

    raw_content = completion.choices[0].message.content or ""
    parsed = _safe_json_loads(raw_content)
    if not parsed:
        return fallback, "heuristic", None

    alternative_location_id = str(parsed.get("alternative_location_id", "")).strip()
    if not alternative_location_id:
        return fallback, "heuristic", None

    selected = next((candidate for candidate in candidates if candidate["location_id"] == alternative_location_id), None)
    if not selected:
        return fallback, "heuristic", None

    reason = str(parsed.get("reason", "")).strip() or None
    return selected, "openai", reason


def _build_nearby_locations(
    predictions: list[dict[str, Any]],
    user_lat: float,
    user_lng: float,
    radius_km: float,
) -> list[dict[str, Any]]:
    nearby: list[dict[str, Any]] = []
    for item in predictions:
        latitude = _to_float(item.get("latitude"))
        longitude = _to_float(item.get("longitude"))
        distance_km = round(_haversine_km(user_lat, user_lng, latitude, longitude), 2)

        if distance_km <= radius_km:
            nearby.append(
                {
                    "location_id": str(item.get("locationId", "")),
                    "location_name": str(item.get("locationName", "Unknown")),
                    "latitude": latitude,
                    "longitude": longitude,
                    "distance_km": distance_km,
                    "predicted_density": round(_to_float(item.get("crowdDensity")), 2),
                    "status": str(item.get("status", "low")),
                }
            )

    nearby.sort(key=lambda row: row["distance_km"])
    return nearby


async def get_smart_route_nearby(latitude: float, longitude: float, radius_km: float | None = None) -> dict[str, Any]:
    effective_radius_km = _normalized_radius(radius_km)
    predictions = get_bulk_predictions(hour=None)
    nearby_locations = _build_nearby_locations(predictions, latitude, longitude, effective_radius_km)

    suggestions: list[dict[str, Any]] = []

    for crowded in nearby_locations:
        if crowded["predicted_density"] < float(HIGH_DENSITY_THRESHOLD):
            continue

        alternatives = [
            loc
            for loc in nearby_locations
            if loc["location_id"] != crowded["location_id"] and loc["predicted_density"] < crowded["predicted_density"]
        ]
        if not alternatives:
            continue

        alternatives.sort(key=lambda loc: (loc["predicted_density"], loc["distance_km"]))
        candidates = alternatives[:MAX_CANDIDATES_PER_LOCATION]

        enriched_candidates: list[dict[str, Any]] = []
        for candidate in candidates:
            route_metrics = _build_route_metrics(latitude, longitude, candidate["latitude"], candidate["longitude"])
            enriched_candidates.append(
                {
                    **candidate,
                    **route_metrics,
                }
            )

        selected, selection_source, ai_reason = await _select_fastest_candidate_with_openai(
            user_lat=latitude,
            user_lng=longitude,
            original=crowded,
            candidates=enriched_candidates,
        )

        suggestions.append(
            {
                "original_location_id": crowded["location_id"],
                "original_location_name": crowded["location_name"],
                "original_density": crowded["predicted_density"],
                "original_distance_km": crowded["distance_km"],
                "alternative_location_id": selected["location_id"],
                "alternative_location_name": selected["location_name"],
                "alternative_density": selected["predicted_density"],
                "alternative_distance_km": selected["distance_km"],
                "savings": round(crowded["predicted_density"] - selected["predicted_density"], 2),
                "fastest_route_minutes": round(_to_float(selected.get("route_duration_minutes")), 1),
                "fastest_route_distance_km": round(_to_float(selected.get("route_distance_km")), 2),
                "route_source": str(selected.get("route_source", "haversine_fallback")),
                "selection_source": selection_source,
                "ai_reason": ai_reason,
            }
        )

    public_nearby_locations = [
        {
            "location_id": location["location_id"],
            "location_name": location["location_name"],
            "distance_km": location["distance_km"],
            "predicted_density": location["predicted_density"],
            "status": location["status"],
        }
        for location in nearby_locations
    ]

    return {
        "radius_km": effective_radius_km,
        "nearby_locations": public_nearby_locations,
        "suggestions": suggestions,
    }
