from fastapi import APIRouter

from app.data.locations import SEEDED_LOCATIONS

router = APIRouter()


@router.get("")
async def list_locations() -> list[dict]:
    return SEEDED_LOCATIONS