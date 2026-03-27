"""
Crowd Prediction Service
─────────────────────────────────────────────────────────────────────
Uses a trained GradientBoostingRegressor per location to predict
crowd density (0-100) based on: hour, day_of_week, is_weekend,
is_holiday, location_type_encoded, and interaction features.
"""

import numpy as np
import joblib
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crowd_model.joblib")
MODEL_VERSION = "1.0.0"

# Location type → numeric encoding
LOCATION_TYPE_ENC = {
    "metro": 0,
    "bus": 1,
    "mall": 2,
    "park": 3,
    "railway": 4,
}

# Mumbai-specific crowd patterns per location type
# Format: {hour: base_density} - these are realistic Mumbai patterns
CROWD_PATTERNS: Dict[str, Dict[int, float]] = {
    "metro": {
        0: 2, 1: 1, 2: 1, 3: 1, 4: 3, 5: 15,
        6: 45, 7: 75, 8: 92, 9: 85, 10: 55, 11: 50,
        12: 60, 13: 55, 14: 45, 15: 48, 16: 52, 17: 78,
        18: 90, 19: 88, 20: 72, 21: 55, 22: 35, 23: 15,
    },
    "bus": {
        0: 3, 1: 2, 2: 1, 3: 2, 4: 5, 5: 20,
        6: 50, 7: 70, 8: 85, 9: 80, 10: 60, 11: 55,
        12: 65, 13: 60, 14: 50, 15: 55, 16: 60, 17: 80,
        18: 88, 19: 82, 20: 68, 21: 50, 22: 30, 23: 12,
    },
    "mall": {
        0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2,
        6: 5, 7: 8, 8: 15, 9: 20, 10: 35, 11: 55,
        12: 72, 13: 75, 14: 70, 15: 78, 16: 85, 17: 88,
        18: 92, 19: 90, 20: 82, 21: 60, 22: 30, 23: 8,
    },
    "park": {
        0: 1, 1: 1, 2: 1, 3: 1, 4: 3, 5: 18,
        6: 45, 7: 60, 8: 50, 9: 40, 10: 35, 11: 30,
        12: 20, 13: 18, 14: 15, 15: 20, 16: 35, 17: 55,
        18: 65, 19: 58, 20: 40, 21: 25, 22: 10, 23: 3,
    },
    "railway": {
        0: 5, 1: 3, 2: 2, 3: 3, 4: 8, 5: 25,
        6: 55, 7: 80, 8: 90, 9: 82, 10: 65, 11: 60,
        12: 68, 13: 65, 14: 55, 15: 58, 16: 62, 17: 82,
        18: 92, 19: 88, 20: 75, 21: 60, 22: 40, 23: 20,
    },
}

# Per-location offsets to differentiate metro_a vs metro_b etc.
LOCATION_OFFSETS = {
    "metro_a": +5,
    "metro_b": -3,
    "bus_stop_1": 0,
    "mall_1": +2,
    "park_1": -5,
    "station_1": +8,
}

# Weekend multipliers per location type
WEEKEND_MULTIPLIERS = {
    "metro": 0.65,
    "bus": 0.60,
    "mall": 1.35,
    "park": 1.40,
    "railway": 0.80,
}


class CrowdPredictionService:
    """Manages model training, persistence, and inference."""

    def __init__(self):
        self.models: Dict[str, GradientBoostingRegressor] = {}
        self.model_version = MODEL_VERSION
        self.trained_at: Optional[datetime] = None
        self.is_loaded = False
        self._load_or_train()

    # ── Features ──────────────────────────────────────────────────────────────

    def _make_features(
        self,
        hour: int,
        day_of_week: int,
        is_holiday: bool,
        location_type: str,
    ) -> np.ndarray:
        is_weekend = int(day_of_week >= 5)
        is_peak_morning = int(7 <= hour <= 9)
        is_peak_evening = int(17 <= hour <= 20)
        is_night = int(hour <= 5 or hour >= 22)
        loc_type_enc = LOCATION_TYPE_ENC.get(location_type, 0)

        return np.array([
            hour,
            day_of_week,
            int(is_weekend),
            int(is_holiday),
            loc_type_enc,
            is_peak_morning,
            is_peak_evening,
            is_night,
            hour * loc_type_enc,           # interaction
            is_weekend * loc_type_enc,     # interaction
        ], dtype=float).reshape(1, -1)

    # ── Synthetic Training Data ────────────────────────────────────────────────

    def _generate_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ~5000 synthetic but realistic samples for Mumbai crowds.
        """
        X, y = [], []
        rng = np.random.default_rng(42)

        location_types = list(CROWD_PATTERNS.keys())

        for _ in range(5000):
            loc_type = rng.choice(location_types)
            hour = rng.integers(0, 24)
            day_of_week = rng.integers(0, 7)
            is_holiday = bool(rng.random() < 0.08)
            is_weekend = day_of_week >= 5

            base = CROWD_PATTERNS[loc_type][hour]

            # Apply weekend modifier
            if is_weekend:
                base *= WEEKEND_MULTIPLIERS[loc_type]

            # Holiday modifier
            if is_holiday:
                if loc_type in ("mall", "park"):
                    base *= 1.30
                else:
                    base *= 0.60

            # Add realistic noise
            noise = rng.normal(0, 6)
            density = float(np.clip(base + noise, 0, 100))

            feat = self._make_features(hour, day_of_week, is_holiday, loc_type)
            X.append(feat[0])
            y.append(density)

        return np.array(X), np.array(y)

    # ── Train ─────────────────────────────────────────────────────────────────

    def train(self) -> Dict:
        """Train one shared GBR model (fast, accurate enough for demo)."""
        logger.info("Training crowd prediction model...")
        X, y = self._generate_training_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.08,
            max_depth=5,
            random_state=42,
            subsample=0.85,
        )
        model.fit(X_train, y_train)

        # Evaluate
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        accuracy = max(0.0, 1.0 - mae / 100.0)

        self.models["shared"] = model
        self.trained_at = datetime.utcnow()
        self.is_loaded = True

        # Persist
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(
            {"model": model, "trained_at": self.trained_at, "mae": mae},
            MODEL_PATH,
        )

        logger.info(f"Model trained. MAE={mae:.2f}, Accuracy={accuracy:.2%}")
        return {
            "accuracy": round(accuracy, 4),
            "mae": round(mae, 2),
            "samples": len(X_train),
        }

    # ── Load ──────────────────────────────────────────────────────────────────

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                saved = joblib.load(MODEL_PATH)
                self.models["shared"] = saved["model"]
                self.trained_at = saved.get("trained_at", datetime.utcnow())
                self.is_loaded = True
                logger.info("Loaded existing crowd model from disk.")
                return
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Retraining.")

        self.train()

    # ── Predict ───────────────────────────────────────────────────────────────

    def predict(
        self,
        location_id: str,
        location_type: str,
        hour: int,
        day_of_week: Optional[int] = None,
        is_holiday: bool = False,
    ) -> Tuple[float, float]:
        """
        Returns (crowd_density 0-100, confidence 0-1).
        Falls back to pattern-based if model not loaded.
        """
        if day_of_week is None:
            day_of_week = datetime.utcnow().weekday()

        if self.is_loaded and "shared" in self.models:
            feat = self._make_features(hour, day_of_week, is_holiday, location_type)
            raw = float(self.models["shared"].predict(feat)[0])

            # Apply per-location fine-tuning offset
            offset = LOCATION_OFFSETS.get(location_id, 0)
            is_weekend = day_of_week >= 5
            density = float(np.clip(raw + offset, 0, 100))

            # Confidence heuristic (higher during peak hours = more data)
            confidence = 0.85 if (7 <= hour <= 9 or 17 <= hour <= 20) else 0.75
            return density, confidence

        # Fallback: pure pattern lookup
        return self._pattern_predict(location_id, location_type, hour, day_of_week, is_holiday)

    def _pattern_predict(
        self,
        location_id: str,
        location_type: str,
        hour: int,
        day_of_week: int,
        is_holiday: bool,
    ) -> Tuple[float, float]:
        base = CROWD_PATTERNS.get(location_type, CROWD_PATTERNS["metro"])[hour]
        if day_of_week >= 5:
            base *= WEEKEND_MULTIPLIERS.get(location_type, 1.0)
        if is_holiday:
            base *= 1.2 if location_type in ("mall", "park") else 0.7
        offset = LOCATION_OFFSETS.get(location_id, 0)
        density = float(np.clip(base + offset, 0, 100))
        return density, 0.60

    def predict_24h(
        self,
        location_id: str,
        location_type: str,
        day_of_week: Optional[int] = None,
        is_holiday: bool = False,
    ) -> List[Tuple[int, float]]:
        """Returns [(hour, density), ...] for all 24 hours."""
        if day_of_week is None:
            day_of_week = datetime.utcnow().weekday()
        return [
            (h, self.predict(location_id, location_type, h, day_of_week, is_holiday)[0])
            for h in range(24)
        ]

    @staticmethod
    def density_to_status(density: float) -> str:
        if density < 40:
            return "low"
        elif density < 70:
            return "medium"
        return "high"

    @staticmethod
    def density_to_count(density: float) -> int:
        """Converts density % to approximate crowd count (mirrors Flutter formula)."""
        return round(density * 5)


# Singleton
prediction_service = CrowdPredictionService()
