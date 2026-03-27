from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Request Schemas ──────────────────────────────────────────────────────────

class BulkPredictRequest(BaseModel):
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="0=Monday, 6=Sunday")
    is_holiday: Optional[bool] = False
    location_ids: Optional[List[str]] = None  # None = all locations


class BestTimeRequest(BaseModel):
    from_location: str = Field(..., alias="from")
    to_location: str = Field(..., alias="to")

    class Config:
        populate_by_name = True


class TrainRequest(BaseModel):
    admin_secret: str
    epochs: Optional[int] = 100


# ─── Response Schemas ─────────────────────────────────────────────────────────

class CrowdPrediction(BaseModel):
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    crowd_count: int
    crowd_density: float          # 0–100
    status: str                   # low | medium | high
    predicted_next_hour: Optional[float] = None
    timestamp: datetime
    confidence: float             # 0–1, model confidence
    source: str                   # "model" | "realtime" | "cached"


class BulkPredictResponse(BaseModel):
    predictions: List[CrowdPrediction]
    model_version: str
    generated_at: datetime
    maps_integrated: bool


class HourSlot(BaseModel):
    hour: int
    label: str                    # "8 AM", "2 PM" etc.
    density_from: float
    density_to: float
    avg_density: float
    status: str


class BestTimeResponse(BaseModel):
    from_location: str
    to_location: str
    best_hour: int
    best_hour_label: str
    expected_density: float
    status: str
    hourly_forecast: List[HourSlot]
    ai_recommendation: str        # OpenAI generated insight
    generated_at: datetime


class RealtimeStatus(BaseModel):
    maps_enabled: bool
    maps_api_key_set: bool
    last_collection: Optional[datetime]
    locations_covered: int
    traffic_data_age_seconds: Optional[int]
    status_message: str


class RealtimeDataPoint(BaseModel):
    location_id: str
    location_name: str
    latitude: float
    longitude: float
    crowd_density: float
    crowd_count: int
    status: str
    traffic_level: Optional[str] = None  # from Google Maps
    nearby_places_count: Optional[int] = None
    source: str
    collected_at: datetime


class RealtimeCollectResponse(BaseModel):
    success: bool
    data: List[RealtimeDataPoint]
    collected_at: datetime
    source: str                   # "google_maps" | "synthetic"


class TrainResponse(BaseModel):
    success: bool
    message: str
    accuracy: Optional[float] = None
    samples_trained: Optional[int] = None
    model_version: str
    trained_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    maps_available: bool
    openai_available: bool
    uptime_seconds: float
