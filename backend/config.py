from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CrowdSense AI Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""

    # Admin
    ADMIN_SECRET: str = "crowdsense-admin-2024"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# ─── Fixed Locations (mirrors Flutter frontend) ───────────────────────────────
LOCATIONS = [
    {
        "id": "metro_a",
        "name": "Metro Station A",
        "lat": 19.0760,
        "lng": 72.8777,
        "type": "metro",
        "place_id": None,  # set via Google Maps if needed
    },
    {
        "id": "metro_b",
        "name": "Metro Station B",
        "lat": 19.0590,
        "lng": 72.8360,
        "type": "metro",
        "place_id": None,
    },
    {
        "id": "bus_stop_1",
        "name": "Central Bus Stop",
        "lat": 19.0820,
        "lng": 72.8810,
        "type": "bus",
        "place_id": None,
    },
    {
        "id": "mall_1",
        "name": "City Mall",
        "lat": 19.0650,
        "lng": 72.8650,
        "type": "mall",
        "place_id": None,
    },
    {
        "id": "park_1",
        "name": "Green Park",
        "lat": 19.0700,
        "lng": 72.8500,
        "type": "park",
        "place_id": None,
    },
    {
        "id": "station_1",
        "name": "Railway Station",
        "lat": 19.0728,
        "lng": 72.8826,
        "type": "railway",
        "place_id": None,
    },
]

LOCATION_MAP = {loc["id"]: loc for loc in LOCATIONS}
