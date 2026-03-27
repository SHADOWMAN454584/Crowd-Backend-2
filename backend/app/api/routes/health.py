from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def get_health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "openAiConfigured": bool(settings.openai_api_key),
        "googleMapsConfigured": bool(settings.google_maps_api_key),
        "mapProvider": settings.map_provider,
        "realtimeEnabled": settings.enable_realtime_maps,
        "allowedOrigins": settings.allowed_origins,
    }