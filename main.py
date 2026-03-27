"""
CrowdSense AI — FastAPI Backend
═══════════════════════════════════════════════════════════════════════
Entry point. Configures the app, registers routers, initialises services.

Start with:
    uvicorn main:app --reload --port 8000

Or with custom API base:
    flutter run --dart-define=API_BASE_URL=http://localhost:8000
"""

import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from schemas import HealthResponse
import prediction_service as _pred_module
import maps_service as _maps_module
import ai_service as _ai_module

# ── Routers ────────────────────────────────────────────────────────────────────
import predict, best_time, realtime, admin

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("crowdsense")

START_TIME = time.time()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup:
      1. Initialise (or load) the ML prediction model
      2. Initialise Google Maps client
      3. Initialise OpenAI client
    """
    logger.info("═" * 60)
    logger.info(" CrowdSense AI Backend starting up…")
    logger.info("═" * 60)

    # ML model (auto-trains on first run, loads from disk on subsequent runs)
    from services.prediction_service import prediction_service
    logger.info(f"✔  ML model loaded (version {prediction_service.model_version})")

    # Google Maps
    maps = _maps_module.init_maps_service(settings.GOOGLE_MAPS_API_KEY)
    if maps.enabled:
        logger.info("✔  Google Maps API connected")
    else:
        logger.warning("⚠  Google Maps API key not set — using ML predictions only")

    # OpenAI
    ai = _ai_module.init_ai_service(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
    if ai.enabled:
        logger.info(f"✔  OpenAI connected ({settings.OPENAI_MODEL})")
    else:
        logger.warning("⚠  OpenAI API key not set — using rule-based fallbacks")

    logger.info("═" * 60)
    logger.info(" Ready. Listening on http://0.0.0.0:8000")
    logger.info("═" * 60)

    yield  # App runs here

    logger.info("CrowdSense AI shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CrowdSense AI API",
    description=(
        "Backend for the CrowdSense AI Flutter app. "
        "Provides ML-powered crowd predictions, Google Maps integration, "
        "and OpenAI-generated travel recommendations for Mumbai locations."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (required for Flutter Web) ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Lightweight health check polled every 30 seconds by the Flutter app.
    Returns service availability flags and uptime.
    """
    from services.prediction_service import prediction_service
    from services.maps_service import maps_service
    from services.ai_service import ai_service

    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        model_loaded=prediction_service.is_loaded,
        maps_available=maps_service is not None and maps_service.enabled,
        openai_available=ai_service is not None and ai_service.enabled,
        uptime_seconds=round(time.time() - START_TIME, 1),
    )


# ── Register Routers ───────────────────────────────────────────────────────────
app.include_router(predict.router)
app.include_router(best_time.router)
app.include_router(realtime.router)
app.include_router(admin.router)


# ── Root redirect ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(
        content={
            "app": "CrowdSense AI API",
            "version": settings.VERSION,
            "docs": "/docs",
            "health": "/health",
        }
    )


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
