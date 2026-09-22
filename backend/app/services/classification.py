"""Lógica de clasificación aprobado / rechazado / desconocido."""

from dataclasses import dataclass

from backend.app.core.constants import (
    CLASS_ID_CRACK,
    CLASS_ID_EGG,
    REASON_CRACK,
    REASON_NO_CRACK,
    REASON_NO_EGG,
    ROUTE_ACCEPT,
    ROUTE_REJECT,
    ROUTE_REVIEW,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_UNKNOWN,
)


@dataclass(frozen=True)
class DetectionLike:
    """Contrato mínimo para clasificación (sin depender de YOLO)."""

    class_id: int
    class_name: str
    confidence: float


@dataclass(frozen=True)
class ClassificationResult:
    status: str
    route: str
    reason: str
    egg_detected: bool
    crack_detected: bool


def classify_detections(
    detections: list[DetectionLike],
    crack_confidence_threshold: float,
) -> ClassificationResult:
    """Determina estado operativo a partir de detecciones del modelo.

    Reglas:
    - ``rejected`` si hay ``crack`` con confidence >= crack_confidence_threshold.
    - ``approved`` si hay ``egg`` y no hay crack válido.
    - ``unknown`` si no hay ``egg``.

    Nota: ``approved`` significa solo "huevo detectado sin grieta visible según este
    modelo". No implica calidad comercial, peso, suciedad ni otras clases ausentes
    en INDIGO.
    """
    egg_detected = any(d.class_id == CLASS_ID_EGG or d.class_name == "egg" for d in detections)
    valid_cracks = [
        d
        for d in detections
        if (d.class_id == CLASS_ID_CRACK or d.class_name == "crack")
        and d.confidence >= crack_confidence_threshold
    ]
    crack_detected = len(valid_cracks) > 0

    if crack_detected:
        return ClassificationResult(
            status=STATUS_REJECTED,
            route=ROUTE_REJECT,
            reason=REASON_CRACK,
            egg_detected=egg_detected,
            crack_detected=True,
        )

    if egg_detected:
        return ClassificationResult(
            status=STATUS_APPROVED,
            route=ROUTE_ACCEPT,
            reason=REASON_NO_CRACK,
            egg_detected=True,
            crack_detected=False,
        )

    return ClassificationResult(
        status=STATUS_UNKNOWN,
        route=ROUTE_REVIEW,
        reason=REASON_NO_EGG,
        egg_detected=False,
        crack_detected=False,
    )
