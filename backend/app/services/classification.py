"""Lógica de clasificación aprobado / rechazado / desconocido."""

from dataclasses import dataclass

from backend.app.core.constants import (
    REASON_CRACK,
    REASON_CRACK_WITHOUT_EGG,
    REASON_NO_CRACK,
    REASON_NO_EGG,
    ROUTE_ACCEPT,
    ROUTE_REJECT,
    ROUTE_REVIEW,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_UNKNOWN,
)
from backend.app.services.detection_filter import is_valid_crack, is_valid_egg
from backend.app.services.detection_types import DetectionLike

__all__ = [
    "ClassificationResult",
    "DetectionLike",
    "classify_detections",
    "classify_primary_egg",
]


@dataclass(frozen=True)
class ClassificationResult:
    status: str
    route: str
    reason: str
    egg_detected: bool
    crack_detected: bool


def classify_primary_egg(
    has_primary_egg: bool,
    associated_cracks: list[DetectionLike],
    crack_confidence_threshold: float,
) -> ClassificationResult:
    """Clasifica usando primary_egg y cracks espacialmente asociados."""
    egg_detected = has_primary_egg
    crack_detected = any(
        is_valid_crack(detection, crack_confidence_threshold) for detection in associated_cracks
    )

    if crack_detected and not egg_detected:
        return ClassificationResult(
            status=STATUS_UNKNOWN,
            route=ROUTE_REVIEW,
            reason=REASON_CRACK_WITHOUT_EGG,
            egg_detected=False,
            crack_detected=True,
        )

    if crack_detected:
        return ClassificationResult(
            status=STATUS_REJECTED,
            route=ROUTE_REJECT,
            reason=REASON_CRACK,
            egg_detected=True,
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


def classify_detections(
    detections: list[DetectionLike],
    egg_confidence_threshold: float,
    crack_confidence_threshold: float,
) -> ClassificationResult:
    """Determina estado operativo a partir de detecciones del modelo.

    Reglas:
    - ``rejected`` si hay ``egg`` válido y ``crack`` válido.
    - ``unknown`` / ``review`` si hay ``crack`` válido pero no hay ``egg`` válido.
    - ``approved`` si hay ``egg`` válido y no hay crack válido.
    - ``unknown`` si no hay ``egg`` ni crack válido.

    Nota: ``approved`` significa solo "huevo detectado sin grieta visible según este
    modelo". No implica calidad comercial, peso, suciedad ni otras clases ausentes
    en INDIGO.
    """
    egg_detected = any(is_valid_egg(d, egg_confidence_threshold) for d in detections)
    crack_detected = any(is_valid_crack(d, crack_confidence_threshold) for d in detections)

    if crack_detected and not egg_detected:
        return ClassificationResult(
            status=STATUS_UNKNOWN,
            route=ROUTE_REVIEW,
            reason=REASON_CRACK_WITHOUT_EGG,
            egg_detected=False,
            crack_detected=True,
        )

    if crack_detected:
        return ClassificationResult(
            status=STATUS_REJECTED,
            route=ROUTE_REJECT,
            reason=REASON_CRACK,
            egg_detected=True,
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
