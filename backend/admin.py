"""
/admin routes
─────────────────────────────────────────────────────────────────────
POST /realtime/train  →  Retrain the ML model (admin only)

Protected by admin secret header/body.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

from models.schemas import TrainRequest, TrainResponse
from services.prediction_service import prediction_service
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/realtime", tags=["Admin"])


@router.post("/train", response_model=TrainResponse)
async def retrain_model(body: TrainRequest):
    """
    Triggers a full retraining of the crowd prediction model.
    Requires admin_secret to match the server's configured secret.

    Returns accuracy metrics and new model version.
    """
    if body.admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret.")

    try:
        logger.info(f"Admin triggered model retraining (epochs={body.epochs})")
        metrics = prediction_service.train()

        return TrainResponse(
            success=True,
            message=f"Model retrained successfully on {metrics['samples']} samples.",
            accuracy=metrics["accuracy"],
            samples_trained=metrics["samples"],
            model_version=prediction_service.model_version,
            trained_at=prediction_service.trained_at or datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")
