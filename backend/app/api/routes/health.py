"""Health check — no ejecuta inferencia."""

from fastapi import APIRouter

from backend.app.core.constants import MODEL_IMGSZ, MODEL_NAME, SERVICE_NAME
from backend.app.schemas.prediction import HealthResponse
from backend.app.services.inference import get_inference_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    service = get_inference_service()
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        model_loaded=service.is_loaded,
        model=MODEL_NAME,
        input_size=MODEL_IMGSZ,
        model_path=str(service.model_path) if service.model_path else None,
        model_error=service.load_error if not service.is_loaded else None,
    )
