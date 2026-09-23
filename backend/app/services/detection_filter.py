"""Filtrado post-YOLO por umbral de confianza por clase."""

from backend.app.core.constants import CLASS_ID_CRACK, CLASS_ID_EGG
from backend.app.services.detection_types import DetectionLike


def is_valid_egg(detection: DetectionLike, egg_confidence_threshold: float) -> bool:
    return (
        detection.class_id == CLASS_ID_EGG or detection.class_name == "egg"
    ) and detection.confidence >= egg_confidence_threshold


def is_valid_crack(detection: DetectionLike, crack_confidence_threshold: float) -> bool:
    return (
        detection.class_id == CLASS_ID_CRACK or detection.class_name == "crack"
    ) and detection.confidence >= crack_confidence_threshold


def filter_valid_detections(
    detections: list[DetectionLike],
    egg_confidence_threshold: float,
    crack_confidence_threshold: float,
) -> list[DetectionLike]:
    """Conserva solo detecciones que superan el umbral de su clase."""
    return [
        detection
        for detection in detections
        if is_valid_egg(detection, egg_confidence_threshold)
        or is_valid_crack(detection, crack_confidence_threshold)
    ]
