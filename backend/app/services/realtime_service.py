from __future__ import annotations

from typing import Any

try:
    from app.core.config import settings
except Exception:
    settings = None

from app.services.cache_service import get_cached_realtime_payload, set_cached_realtime_payload
from app.services.prediction_service import get_bulk_predictions


def get_realtime_status() -> dict[str, Any]:
    cached = get_cached_realtime_payload()
    return {
        "enabled": bool(getattr(settings, "ENABLE_REALTIME_MAPS", False)) if settings else False,
        "provider": getattr(settings, "MAP_PROVIDER", "mock") if settings else "mock",
        "lastUpdated": cached.get("timestamp"),
    }


async def collect_realtime_data() -> dict[str, Any]:
    try:
        predictions = get_bulk_predictions()
        cached = set_cached_realtime_payload(predictions)
        return {
            "items": cached["items"],
            "timestamp": cached["timestamp"],
            "provider": getattr(settings, "MAP_PROVIDER", "mock") if settings else "mock",
            "isLive": bool(getattr(settings, "ENABLE_REALTIME_MAPS", False)) if settings else False,
        }
    except Exception:
        cached = get_cached_realtime_payload()
        return {
            "items": cached.get("items", []),
            "timestamp": cached.get("timestamp"),
            "provider": "cache",
            "isLive": False,
        }