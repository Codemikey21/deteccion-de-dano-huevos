"""Tipos compartidos para detecciones."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionLike:
    """Contrato mínimo para clasificación y filtrado post-YOLO."""

    class_id: int
    class_name: str
    confidence: float
