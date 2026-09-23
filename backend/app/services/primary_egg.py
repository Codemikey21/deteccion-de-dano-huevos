"""Selección de primary_egg y cracks asociados para flujo single-egg."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.core.constants import CLASS_ID_CRACK, CLASS_ID_EGG
from backend.app.schemas.prediction import BoundingBox, Detection, NormalizedBBox, PrimaryEgg
from backend.app.services.bbox_utils import (
    bbox_metrics,
    is_crack_near_egg,
    normalize_bbox,
    sanitize_bbox,
)
from backend.app.services.inference import RawDetection

PRIMARY_EGG_MIN_CONFIDENCE = 0.30
IMPOSSIBLE_AREA_RATIO = 0.98
PREFERRED_MIN_ASPECT = 0.45
PREFERRED_MAX_ASPECT = 2.2
CRACK_NEAR_EGG_EXPANSION = 1.15
RAW_CRACK_MIN = 0.25


@dataclass(frozen=True)
class PrimaryEggSelection:
    primary_egg: PrimaryEgg | None
    associated_cracks: list[Detection]


def _is_impossible_geometry(bbox: BoundingBox, image_width: int, image_height: int) -> bool:
    metrics = bbox_metrics(bbox, image_width, image_height)
    if metrics.width <= 0 or metrics.height <= 0:
        return True
    if metrics.area_ratio >= IMPOSSIBLE_AREA_RATIO:
        return True
    if bbox.x1 < -1 or bbox.y1 < -1 or bbox.x2 > image_width + 1 or bbox.y2 > image_height + 1:
        return True
    return False


def _geometry_score(bbox: BoundingBox, image_width: int, image_height: int) -> float:
    """Plausibilidad geométrica como score suave, no como filtro agresivo."""
    metrics = bbox_metrics(bbox, image_width, image_height)
    score = 1.0

    if metrics.area_ratio > 0.95:
        score *= 0.5
    elif metrics.area_ratio > 0.85:
        score *= 0.85

    if metrics.aspect_ratio < PREFERRED_MIN_ASPECT or metrics.aspect_ratio > PREFERRED_MAX_ASPECT:
        score *= 0.75

    return score


def _candidate_score(raw: RawDetection, image_width: int, image_height: int) -> float:
    if raw.class_id != CLASS_ID_EGG and raw.class_name != "egg":
        return -1.0
    if raw.confidence < PRIMARY_EGG_MIN_CONFIDENCE:
        return -1.0

    bbox = BoundingBox(x1=raw.x1, y1=raw.y1, x2=raw.x2, y2=raw.y2)
    sanitized = sanitize_bbox(bbox, image_width, image_height)
    if sanitized is None or _is_impossible_geometry(sanitized, image_width, image_height):
        return -1.0

    geometry = _geometry_score(sanitized, image_width, image_height)
    return raw.confidence * geometry


def _to_detection(raw: RawDetection, image_width: int, image_height: int) -> Detection:
    bbox = BoundingBox(x1=raw.x1, y1=raw.y1, x2=raw.x2, y2=raw.y2)
    sanitized = sanitize_bbox(bbox, image_width, image_height) or bbox
    return Detection(
        class_id=raw.class_id,
        class_name=raw.class_name,
        confidence=raw.confidence,
        bbox=sanitized,
        bbox_normalized=normalize_bbox(sanitized, image_width, image_height),
    )


def select_primary_egg(
    raw_detections: list[RawDetection],
    image_width: int,
    image_height: int,
) -> PrimaryEgg | None:
    """Elige el egg candidato con mejor score (confidence * plausibilidad)."""
    best_raw: RawDetection | None = None
    best_score = -1.0

    for raw in raw_detections:
        score = _candidate_score(raw, image_width, image_height)
        if score > best_score:
            best_score = score
            best_raw = raw

    if best_raw is None:
        return None

    bbox = BoundingBox(x1=best_raw.x1, y1=best_raw.y1, x2=best_raw.x2, y2=best_raw.y2)
    sanitized = sanitize_bbox(bbox, image_width, image_height)
    if sanitized is None:
        return None

    return PrimaryEgg(
        confidence=best_raw.confidence,
        bbox=sanitized,
        bbox_normalized=normalize_bbox(sanitized, image_width, image_height),
    )


def get_associated_cracks(
    raw_detections: list[RawDetection],
    primary_egg: PrimaryEgg,
    image_width: int,
    image_height: int,
) -> list[Detection]:
    """Cracks relevantes espacialmente al primary_egg."""
    associated: list[Detection] = []

    for raw in raw_detections:
        if raw.class_id != CLASS_ID_CRACK and raw.class_name != "crack":
            continue
        if raw.confidence < RAW_CRACK_MIN:
            continue

        crack_bbox = BoundingBox(x1=raw.x1, y1=raw.y1, x2=raw.x2, y2=raw.y2)
        if not is_crack_near_egg(crack_bbox, primary_egg.bbox, CRACK_NEAR_EGG_EXPANSION):
            continue

        associated.append(_to_detection(raw, image_width, image_height))

    associated.sort(key=lambda detection: detection.confidence, reverse=True)
    return associated


def build_primary_egg_selection(
    raw_detections: list[RawDetection],
    image_width: int,
    image_height: int,
) -> PrimaryEggSelection:
    primary_egg = select_primary_egg(raw_detections, image_width, image_height)
    if primary_egg is None:
        return PrimaryEggSelection(primary_egg=None, associated_cracks=[])

    cracks = get_associated_cracks(raw_detections, primary_egg, image_width, image_height)
    return PrimaryEggSelection(primary_egg=primary_egg, associated_cracks=cracks)
