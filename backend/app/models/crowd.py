"""Crowd-related API models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CrowdData(BaseModel):
    """Frontend-aligned crowd data contract."""

    locationId: str
    locationName: str
    latitude: float
    longitude: float
    crowdCount: int
    crowdDensity: float
    status: str
    timestamp: datetime
    predictedNextHour: float

    model_config = ConfigDict(populate_by_name=True)