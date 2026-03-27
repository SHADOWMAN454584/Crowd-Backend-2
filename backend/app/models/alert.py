"""Alert API models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CrowdAlert(BaseModel):
    """Frontend-aligned crowd alert contract."""

    id: str
    locationId: str
    locationName: str
    threshold: float
    isActive: bool
    createdAt: datetime

    model_config = ConfigDict(populate_by_name=True)