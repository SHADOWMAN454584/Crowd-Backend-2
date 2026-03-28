from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ai import router as ai_router
from app.api.routes.health import router as health_router
from app.api.routes.locations import router as locations_router
from app.api.routes.maps import router as maps_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.realtime import router as realtime_router
from app.api.routes.smart_route import router as smart_route_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Population density backend with prediction, realtime map signals, and AI insights.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])
app.include_router(locations_router, prefix="/locations", tags=["locations"])
app.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
app.include_router(realtime_router, prefix="/realtime", tags=["realtime"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(maps_router, prefix="/maps", tags=["maps"])
app.include_router(smart_route_router, prefix="/smart-route", tags=["smart-route"])


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "message": "Population Density FastAPI backend is running.",
        "docs": "/docs",
        "health": "/health",
    }
