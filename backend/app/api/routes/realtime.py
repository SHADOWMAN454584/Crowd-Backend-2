from fastapi import APIRouter

from app.core.config import settings
from app.services.realtime_service import collect_realtime_data, get_realtime_status
from app.services.cache_service import get_cached_realtime_data

router = APIRouter()


@router.get("/status")
async def realtime_status() -> dict:
    status = get_realtime_status()
    return {
        "enabled": settings.enable_realtime_maps,
        "provider": settings.map_provider,
        "lastUpdated": status.get("lastUpdated"),
    }


@router.post("/collect")
async def realtime_collect() -> dict:
    return await collect_realtime_data()


@router.get("/cached")
async def realtime_cached() -> dict:
    cached = get_cached_realtime_data()
    if cached:
        return cached

    return {
        "provider": settings.map_provider,
        "lastUpdated": None,
        "data": [],
    }