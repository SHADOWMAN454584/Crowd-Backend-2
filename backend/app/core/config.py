"""Application configuration powered by pydantic-settings."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import DEFAULT_OPENAI_MODEL, DEFAULT_REALTIME_PROVIDER


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = Field(default="Population Density API", alias="APP_NAME")
    api_v1_str: str = Field(default="/api/v1", alias="API_V1_STR")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default=DEFAULT_OPENAI_MODEL, alias="OPENAI_MODEL")
    google_maps_api_key: str | None = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    allowed_origins_raw: str | list[str] = Field(default="*", alias="ALLOWED_ORIGINS")
    map_provider: str = Field(default=DEFAULT_REALTIME_PROVIDER, alias="MAP_PROVIDER")
    osm_routing_url: str = Field(
        default="https://router.project-osrm.org/route/v1/driving",
        alias="OSM_ROUTING_URL",
    )
    enable_realtime_maps: bool = Field(default=True, alias="ENABLE_REALTIME_MAPS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("allowed_origins_raw", mode="before")
    @classmethod
    def validate_allowed_origins_raw(cls, value: Any) -> str | list[str]:
        if value is None or value == "":
            return "*"
        return value

    @cached_property
    def allowed_origins(self) -> list[str]:
        raw_value = self.allowed_origins_raw
        if isinstance(raw_value, list):
            return raw_value
        if raw_value.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def google_maps_configured(self) -> bool:
        return bool(self.google_maps_api_key)


settings = Settings()