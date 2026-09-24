"""Utilidades geométricas para bounding boxes."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.schemas.prediction import BoundingBox, NormalizedBBox


@dataclass(frozen=True)
class BBoxMetrics:
    width: float
    height: float
    area: float
    area_ratio: float
    aspect_ratio: float


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def sanitize_bbox(bbox: BoundingBox, image_width: int, image_height: int) -> BoundingBox | None:
    x1 = min(bbox.x1, bbox.x2)
    x2 = max(bbox.x1, bbox.x2)
    y1 = min(bbox.y1, bbox.y2)
    y2 = max(bbox.y1, bbox.y2)

    clamped = BoundingBox(
        x1=max(0.0, min(x1, float(image_width))),
        y1=max(0.0, min(y1, float(image_height))),
        x2=max(0.0, min(x2, float(image_width))),
        y2=max(0.0, min(y2, float(image_height))),
    )

    if clamped.x2 - clamped.x1 < 1.0 or clamped.y2 - clamped.y1 < 1.0:
        return None

    return clamped


def bbox_metrics(bbox: BoundingBox, image_width: int, image_height: int) -> BBoxMetrics:
    width = max(0.0, bbox.x2 - bbox.x1)
    height = max(0.0, bbox.y2 - bbox.y1)
    area = width * height
    image_area = max(float(image_width * image_height), 1.0)
    aspect_ratio = width / height if height > 0 else 0.0
    return BBoxMetrics(
        width=width,
        height=height,
        area=area,
        area_ratio=area / image_area,
        aspect_ratio=aspect_ratio,
    )


def normalize_bbox(bbox: BoundingBox, image_width: int, image_height: int) -> NormalizedBBox:
    width = max(float(image_width), 1.0)
    height = max(float(image_height), 1.0)
    return NormalizedBBox(
        x1=clamp(bbox.x1 / width),
        y1=clamp(bbox.y1 / height),
        x2=clamp(bbox.x2 / width),
        y2=clamp(bbox.y2 / height),
    )


def expand_bbox(bbox: BoundingBox, factor: float) -> BoundingBox:
    center_x = (bbox.x1 + bbox.x2) / 2.0
    center_y = (bbox.y1 + bbox.y2) / 2.0
    half_width = ((bbox.x2 - bbox.x1) * factor) / 2.0
    half_height = ((bbox.y2 - bbox.y1) * factor) / 2.0
    return BoundingBox(
        x1=center_x - half_width,
        y1=center_y - half_height,
        x2=center_x + half_width,
        y2=center_y + half_height,
    )


def bbox_overlap_area(a: BoundingBox, b: BoundingBox) -> float:
    x1 = max(a.x1, b.x1)
    y1 = max(a.y1, b.y1)
    x2 = min(a.x2, b.x2)
    y2 = min(a.y2, b.y2)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return (x2 - x1) * (y2 - y1)


def bbox_iou(a: BoundingBox, b: BoundingBox) -> float:
    overlap = bbox_overlap_area(a, b)
    if overlap <= 0.0:
        return 0.0

    area_a = max((a.x2 - a.x1) * (a.y2 - a.y1), 0.0)
    area_b = max((b.x2 - b.x1) * (b.y2 - b.y1), 0.0)
    union = area_a + area_b - overlap
    return overlap / union if union > 0 else 0.0


def is_crack_near_egg(crack_bbox: BoundingBox, egg_bbox: BoundingBox, expansion: float = 1.15) -> bool:
    expanded = expand_bbox(egg_bbox, expansion)
    center_x = (crack_bbox.x1 + crack_bbox.x2) / 2.0
    center_y = (crack_bbox.y1 + crack_bbox.y2) / 2.0

    if (
        expanded.x1 <= center_x <= expanded.x2
        and expanded.y1 <= center_y <= expanded.y2
    ):
        return True

    crack_area = max((crack_bbox.x2 - crack_bbox.x1) * (crack_bbox.y2 - crack_bbox.y1), 0.0)
    if crack_area <= 0.0:
        return False

    return bbox_overlap_area(crack_bbox, expanded) / crack_area >= 0.25
