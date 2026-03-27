"""Shared constants for crowd prediction and realtime behavior."""

from __future__ import annotations

from datetime import datetime

STATUS_LOW_MAX = 39.99
STATUS_MEDIUM_MAX = 69.99

LOW_STATUS = "low"
MEDIUM_STATUS = "medium"
HIGH_STATUS = "high"

# Density thresholds
LOW_DENSITY_THRESHOLD = 40.0
HIGH_DENSITY_THRESHOLD = 70.0

# Defaults
DEFAULT_PREDICTION_HOUR = datetime.now().hour
DEFAULT_CACHE_TTL_SECONDS = 300
DEFAULT_PREDICTION_HORIZON_HOURS = 1
DEFAULT_REALTIME_REFRESH_SECONDS = 120
DEFAULT_REALTIME_PROVIDER = "mock-osm"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

DENSITY_TO_COUNT_MULTIPLIER = 5
MIN_DENSITY = 0.0
MAX_DENSITY = 100.0