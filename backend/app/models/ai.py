"""AI request and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.crowd import CrowdData


class CrowdPoint(BaseModel):
    """Minimal crowd point payload accepted by AI endpoints."""

    locationId: str
    locationName: str
    crowdDensity: float
    status: str
    timestamp: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)


class AIInsightRequest(BaseModel):
    """Payload for natural language crowd insight generation."""

    hour: int | None = Field(default=None, ge=0, le=23)
    locations: list[CrowdData] | list[CrowdPoint] | None = None
    prompt: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class AIInsightResponse(BaseModel):
    """Response for crowd insight generation."""

    summary: str
    provider: str
    generatedAt: datetime
    basedOnHour: int | None = None

    model_config = ConfigDict(populate_by_name=True)


class RouteAdviceRequest(BaseModel):
    """Payload for route and best-time advice."""

    origin: str | None = None
    destination: str | None = None
    hour: int | None = Field(default=None, ge=0, le=23)
    locations: list[CrowdData] | list[CrowdPoint] | None = None
    preference: Literal["fastest", "least_crowded", "balanced"] = "balanced"

    model_config = ConfigDict(populate_by_name=True)


class RouteAdviceResponse(BaseModel):
    """Response for route advice generation."""

    advice: str
    recommendedDepartureHour: int | None = None
    provider: str
    generatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)