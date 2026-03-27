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
from app.models.user import UserModel

__all__ = [
    "AIInsightRequest",
    "AIInsightResponse",
    "CrowdAlert",
    "CrowdData",
    "CrowdPoint",
    "RouteAdviceRequest",
    "RouteAdviceResponse",
    "UserModel",
]