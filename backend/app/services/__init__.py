"""Service layer exports for the population density backend."""

from app.services.cache_service import get_cached_realtime_payload, set_cached_realtime_payload
from app.services.map_service import get_route_metadata
from app.services.openai_service import generate_insights_summary, generate_route_advice
from app.services.prediction_service import build_crowd_data, get_bulk_predictions
from app.services.realtime_service import collect_realtime_data, get_realtime_status
from app.services.smart_route_service import get_smart_route_nearby

__all__ = [
    "build_crowd_data",
    "collect_realtime_data",
    "generate_insights_summary",
    "generate_route_advice",
    "get_bulk_predictions",
    "get_cached_realtime_payload",
    "get_realtime_status",
    "get_route_metadata",
    "get_smart_route_nearby",
    "set_cached_realtime_payload",
]