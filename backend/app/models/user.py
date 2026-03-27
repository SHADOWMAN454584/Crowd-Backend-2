"""User API models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserModel(BaseModel):
    """Frontend-aligned user contract."""

    id: str
    email: EmailStr
    name: str
    role: str
    createdAt: datetime

    model_config = ConfigDict(populate_by_name=True)