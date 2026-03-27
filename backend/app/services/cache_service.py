from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_CACHE: dict[str, Any] = {
    "items": [],
    "timestamp": None,
}


def set_cached_realtime_payload(items: list[dict[str, Any]]) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    _CACHE["items"] = items
    _CACHE["timestamp"] = timestamp
    return {"items": items, "timestamp": timestamp}


def get_cached_realtime_payload() -> dict[str, Any]:
    return {
        "items": list(_CACHE.get("items") or []),
        "timestamp": _CACHE.get("timestamp"),
    }


def get_cached_realtime_data() -> dict[str, Any]:
    """Alias for get_cached_realtime_payload for API compatibility."""
    payload = get_cached_realtime_payload()
    return {
        "provider": "cache",
        "lastUpdated": payload.get("timestamp"),
        "data": payload.get("items", []),
    }