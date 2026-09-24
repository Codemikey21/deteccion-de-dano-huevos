"""Segunda etapa de inferencia: recorte ROI alrededor del primary_egg.

Objetivo: hacer que cracks pequeños ocupen más resolución efectiva, corriendo
el MISMO modelo YOLO sobre un recorte de la imagen centrado en el huevo
principal, en vez de depender únicamente de la pasada full-frame.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

from PIL import Image

from backend.app.core.constants import CLASS_ID_CRACK
from backend.app.schemas.prediction import BoundingBox, Detection, PrimaryEgg
from backend.app.services.bbox_utils import bbox_iou, clamp, normalize_bbox, sanitize_bbox
from backend.app.services.inference import InferenceOutput, RawDetection

SOURCE_FULL_FRAME = "full_frame"
SOURCE_EGG_ROI = "egg_roi"
SOURCE_BOTH = "both"

DEFAULT_MERGE_IOU_THRESHOLD = 0.5

RunInference = Callable[[Image.Image, float, int], InferenceOutput]


@dataclass(frozen=True)
class TwoStageCrackResult:
    """Resultado de combinar cracks full-frame + ROI para un primary_egg."""

    associated_cracks: list[Detection]
    roi_used: bool
    roi_bbox: BoundingBox | None
    roi_cracks: list[Detection]
    best_roi_crack_confidence: float | None
    crack_source: str | None
    roi_inference_ms: float | None


def compute_roi_bbox(
    egg_bbox: BoundingBox,
    image_width: int,
    image_height: int,
    padding_ratio: float,
) -> BoundingBox:
    """Bbox del primary_egg expandido con padding simétrico y clamp a la imagen.

    Las coordenadas resultantes son enteras (floor/ceil) para que el mismo
    bbox sirva tanto para recortar como para remapear detecciones del recorte
    de vuelta a la imagen original sin desajustes de redondeo.
    """
    width = egg_bbox.x2 - egg_bbox.x1
    height = egg_bbox.y2 - egg_bbox.y1
    pad_x = width * padding_ratio
    pad_y = height * padding_ratio

    x1 = clamp(egg_bbox.x1 - pad_x, 0.0, float(image_width))
    y1 = clamp(egg_bbox.y1 - pad_y, 0.0, float(image_height))
    x2 = clamp(egg_bbox.x2 + pad_x, 0.0, float(image_width))
    y2 = clamp(egg_bbox.y2 + pad_y, 0.0, float(image_height))

    return BoundingBox(
        x1=float(math.floor(x1)),
        y1=float(math.floor(y1)),
        x2=float(min(image_width, math.ceil(x2))),
        y2=float(min(image_height, math.ceil(y2))),
    )


def crop_roi(image: Image.Image, roi_bbox: BoundingBox) -> Image.Image | None:
    """Recorta la región del ROI. None si el recorte resultante es degenerado."""
    x1, y1, x2, y2 = int(roi_bbox.x1), int(roi_bbox.y1), int(roi_bbox.x2), int(roi_bbox.y2)

    if x2 - x1 < 2 or y2 - y1 < 2:
        return None

    return image.crop((x1, y1, x2, y2))


def _remap_to_original(raw: RawDetection, roi_bbox: BoundingBox) -> RawDetection:
    offset_x = roi_bbox.x1
    offset_y = roi_bbox.y1
    return RawDetection(
        class_id=raw.class_id,
        class_name=raw.class_name,
        confidence=raw.confidence,
        x1=raw.x1 + offset_x,
        y1=raw.y1 + offset_y,
        x2=raw.x2 + offset_x,
        y2=raw.y2 + offset_y,
    )


def extract_roi_cracks(
    roi_detections: list[RawDetection],
    roi_bbox: BoundingBox,
    image_width: int,
    image_height: int,
    min_confidence: float,
) -> list[Detection]:
    """Cracks del segundo pase, remapeados a coordenadas de la imagen original.

    Las detecciones de clase egg del segundo pase se ignoran deliberadamente:
    el ROI solo se usa para buscar cracks, nunca para reemplazar primary_egg.
    """
    cracks: list[Detection] = []

    for raw in roi_detections:
        if raw.class_id != CLASS_ID_CRACK and raw.class_name != "crack":
            continue
        if raw.confidence < min_confidence:
            continue

        remapped = _remap_to_original(raw, roi_bbox)
        bbox = BoundingBox(x1=remapped.x1, y1=remapped.y1, x2=remapped.x2, y2=remapped.y2)
        sanitized = sanitize_bbox(bbox, image_width, image_height)
        if sanitized is None:
            continue

        cracks.append(
            Detection(
                class_id=remapped.class_id,
                class_name=remapped.class_name,
                confidence=remapped.confidence,
                bbox=sanitized,
                bbox_normalized=normalize_bbox(sanitized, image_width, image_height),
                crack_source=SOURCE_EGG_ROI,
            )
        )

    cracks.sort(key=lambda detection: detection.confidence, reverse=True)
    return cracks


def merge_crack_detections(
    full_frame_cracks: list[Detection],
    roi_cracks: list[Detection],
    iou_threshold: float = DEFAULT_MERGE_IOU_THRESHOLD,
) -> list[Detection]:
    """Combina cracks full-frame + ROI, deduplicando por IoU (NMS simple).

    Por cada cluster de detecciones solapadas se conserva la de mayor
    confidence, y se etiqueta `crack_source` según qué pasada(s) la vieron.
    """
    candidates: list[tuple[Detection, str]] = [
        (detection, SOURCE_FULL_FRAME) for detection in full_frame_cracks
    ] + [(detection, SOURCE_EGG_ROI) for detection in roi_cracks]
    candidates.sort(key=lambda item: item[0].confidence, reverse=True)

    merged: list[Detection] = []
    sources: list[set[str]] = []

    for detection, source in candidates:
        matched_index = None
        for index, existing in enumerate(merged):
            if bbox_iou(detection.bbox, existing.bbox) >= iou_threshold:
                matched_index = index
                break

        if matched_index is None:
            merged.append(detection)
            sources.append({source})
        else:
            sources[matched_index].add(source)

    result: list[Detection] = []
    for detection, source_set in zip(merged, sources):
        crack_source = SOURCE_BOTH if len(source_set) > 1 else next(iter(source_set))
        result.append(detection.model_copy(update={"crack_source": crack_source}))

    result.sort(key=lambda detection: detection.confidence, reverse=True)
    return result


def _best_source(cracks: list[Detection]) -> str | None:
    if not cracks:
        return None
    return max(cracks, key=lambda detection: detection.confidence).crack_source


def run_egg_roi_crack_pass(
    image: Image.Image,
    primary_egg: PrimaryEgg | None,
    full_frame_associated_cracks: list[Detection],
    image_width: int,
    image_height: int,
    padding_ratio: float,
    min_confidence: float,
    imgsz: int,
    enabled: bool,
    run_inference: RunInference,
) -> TwoStageCrackResult:
    """Orquesta la segunda etapa: ROI crop + inferencia + merge de cracks.

    `run_inference` se inyecta (normalmente `InferenceService.predict_image`)
    para poder testear esta orquestación sin cargar un modelo YOLO real.
    """
    tagged_full_frame = [
        detection.model_copy(update={"crack_source": SOURCE_FULL_FRAME})
        for detection in full_frame_associated_cracks
    ]

    if not enabled or primary_egg is None:
        return TwoStageCrackResult(
            associated_cracks=tagged_full_frame,
            roi_used=False,
            roi_bbox=None,
            roi_cracks=[],
            best_roi_crack_confidence=None,
            crack_source=_best_source(tagged_full_frame),
            roi_inference_ms=None,
        )

    roi_bbox = compute_roi_bbox(primary_egg.bbox, image_width, image_height, padding_ratio)
    cropped = crop_roi(image, roi_bbox)

    if cropped is None:
        return TwoStageCrackResult(
            associated_cracks=tagged_full_frame,
            roi_used=False,
            roi_bbox=None,
            roi_cracks=[],
            best_roi_crack_confidence=None,
            crack_source=_best_source(tagged_full_frame),
            roi_inference_ms=None,
        )

    roi_output = run_inference(cropped, min_confidence, imgsz)
    roi_cracks = extract_roi_cracks(
        roi_output.detections, roi_bbox, image_width, image_height, min_confidence
    )

    merged = merge_crack_detections(tagged_full_frame, roi_cracks)
    best_roi_confidence = roi_cracks[0].confidence if roi_cracks else None

    return TwoStageCrackResult(
        associated_cracks=merged,
        roi_used=True,
        roi_bbox=roi_bbox,
        roi_cracks=roi_cracks,
        best_roi_crack_confidence=best_roi_confidence,
        crack_source=_best_source(merged),
        roi_inference_ms=roi_output.inference_ms,
    )
