"""Endpoint de predicción por imagen."""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.core.config import get_settings
from backend.app.core.constants import ALLOWED_IMAGE_MEDIA_TYPES, MODEL_IMGSZ, MODEL_NAME
from backend.app.schemas.prediction import (
    BoundingBox,
    Detection,
    ImageInfo,
    ModelInfo,
    PredictionResponse,
)
from backend.app.services.classification import classify_detections
from backend.app.services.detection_filter import is_valid_crack, is_valid_egg
from backend.app.services.inference import InvalidImageError, ModelNotLoadedError, get_inference_service

router = APIRouter(tags=["predict"])


def _to_detection(raw) -> Detection:
    return Detection(
        class_id=raw.class_id,
        class_name=raw.class_name,
        confidence=raw.confidence,
        bbox=BoundingBox(x1=raw.x1, y1=raw.y1, x2=raw.x2, y2=raw.y2),
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    settings = get_settings()
    inference = get_inference_service()

    if not inference.is_loaded:
        detail = inference.load_error or "Modelo no cargado"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )

    if file.content_type not in ALLOWED_IMAGE_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo no soportado: {file.content_type}. Use JPEG o PNG.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo vacío",
        )

    try:
        output = inference.predict(
            image_bytes=image_bytes,
            confidence=settings.model_confidence,
            imgsz=MODEL_IMGSZ,
        )
    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ModelNotLoadedError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    raw_detection_likes = [d.to_detection_like() for d in output.detections]
    classification = classify_detections(
        raw_detection_likes,
        egg_confidence_threshold=settings.egg_confidence,
        crack_confidence_threshold=settings.crack_confidence,
    )

    raw_detections = [_to_detection(d) for d in output.detections]
    filtered_detections = [
        _to_detection(raw)
        for raw in output.detections
        if is_valid_egg(raw.to_detection_like(), settings.egg_confidence)
        or is_valid_crack(raw.to_detection_like(), settings.crack_confidence)
    ]

    return PredictionResponse(
        status=classification.status,
        route=classification.route,
        reason=classification.reason,
        egg_detected=classification.egg_detected,
        crack_detected=classification.crack_detected,
        image=ImageInfo(width=output.width, height=output.height),
        raw_detections=raw_detections,
        detections=filtered_detections,
        inference_ms=round(output.inference_ms, 2),
        model=ModelInfo(name=MODEL_NAME, imgsz=MODEL_IMGSZ),
    )
