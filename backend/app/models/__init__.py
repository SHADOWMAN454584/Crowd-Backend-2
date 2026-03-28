"""Pydantic models used across the API."""

from app.models.ai import (
    AIInsightRequest,
    AIInsightResponse,
    CrowdPoint,
    RouteAdviceRequest,
    RouteAdviceResponse,
)
from app.models.alert import CrowdAlert
from app.models.crowd import CrowdData
from app.models.smart_route import (
    NearbySmartLocation,
    SmartRouteNearbyRequest,
    SmartRouteNearbyResponse,
    SmartRouteSuggestion,
)
from app.models.user import UserModel

__all__ = [
    "AIInsightRequest",
    "AIInsightResponse",
    "CrowdAlert",
    "CrowdData",
    "CrowdPoint",
    "RouteAdviceRequest",
    "RouteAdviceResponse",
    "NearbySmartLocation",
    "SmartRouteNearbyRequest",
    "SmartRouteNearbyResponse",
    "SmartRouteSuggestion",
    "UserModel",
]