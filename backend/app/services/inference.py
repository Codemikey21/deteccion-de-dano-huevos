"""Servicio de inferencia YOLO — carga única del checkpoint."""

from __future__ import annotations

import io
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from backend.app.core.constants import CLASS_NAMES, MODEL_IMGSZ
from backend.app.services.detection_types import DetectionLike


class ModelNotLoadedError(RuntimeError):
    """El checkpoint no está cargado o no existe."""


class InvalidImageError(ValueError):
    """La imagen no pudo decodificarse."""


@dataclass(frozen=True)
class RawDetection:
    class_id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

    def to_detection_like(self) -> DetectionLike:
        return DetectionLike(
            class_id=self.class_id,
            class_name=self.class_name,
            confidence=self.confidence,
        )


@dataclass
class InferenceOutput:
    detections: list[RawDetection]
    width: int
    height: int
    inference_ms: float


class InferenceService:
    """Carga YOLO una vez y reutiliza el modelo en cada request."""

    def __init__(self) -> None:
        self._model = None
        self._model_path: Path | None = None
        self._load_error: str | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def load_error(self) -> str | None:
        return self._load_error

    @property
    def model_path(self) -> Path | None:
        return self._model_path

    def load(self, model_path: Path) -> bool:
        """Intenta cargar best.pt. Devuelve False si falla (sin excepción)."""
        self._model_path = model_path
        if not model_path.exists():
            self._model = None
            self._load_error = f"Checkpoint no encontrado: {model_path}"
            return False

        try:
            from ultralytics import YOLO

            self._model = YOLO(str(model_path))
            self._load_error = None
            return True
        except Exception as exc:  # noqa: BLE001
            self._model = None
            self._load_error = f"Error al cargar modelo: {exc}"
            return False

    def predict(
        self,
        image_bytes: bytes,
        confidence: float,
        imgsz: int = MODEL_IMGSZ,
    ) -> InferenceOutput:
        if not self.is_loaded:
            msg = self._load_error or "Modelo no cargado"
            raise ModelNotLoadedError(msg)

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.load()
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError("Imagen corrupta o no decodificable") from exc

        width, height = image.size
        if width <= 0 or height <= 0:
            raise InvalidImageError("Dimensiones de imagen inválidas")

        start = time.perf_counter()
        results = self._model.predict(
            source=image,
            imgsz=imgsz,
            conf=confidence,
            verbose=False,
            save=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        detections: list[RawDetection] = []
        if results:
            result = results[0]
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls_id = int(box.cls.item())
                    conf = float(box.conf.item())
                    x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].tolist())
                    detections.append(
                        RawDetection(
                            class_id=cls_id,
                            class_name=CLASS_NAMES.get(cls_id, str(cls_id)),
                            confidence=conf,
                            x1=x1,
                            y1=y1,
                            x2=x2,
                            y2=y2,
                        )
                    )

        return InferenceOutput(
            detections=detections,
            width=width,
            height=height,
            inference_ms=elapsed_ms,
        )


_inference_service: InferenceService | None = None


def get_inference_service() -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
    return _inference_service
