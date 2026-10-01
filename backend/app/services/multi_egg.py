"""Demo-only dark-line analysis. No additional model calls or learned claims."""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor, isfinite

import cv2
import numpy as np
from PIL import Image

from backend.app.core.config import Settings
from backend.app.schemas.prediction import (
    BoundingBox, Detection, EggResult, EggSummary,
)
from backend.app.services.bbox_utils import bbox_overlap_area, normalize_bbox, sanitize_bbox
from backend.app.services.detection_filter import is_valid_crack, is_valid_egg
from backend.app.services.inference import RawDetection


@dataclass(frozen=True)
class DarkLineResult:
    detected: bool
    area_ratio: float


def analyze_dark_line(roi: Image.Image, settings: Settings) -> DarkLineResult:
    """Look for connected, elongated dark marks inside an inset egg ellipse.

    An absolute threshold AND contrast to the interior median reduce responses
    to uniform brown shells/shadows. The ellipse excludes background/corners.
    This is evidence of a demo mark, never a physical crack diagnosis.
    """
    if min(roi.size) < 12:
        return DarkLineResult(False, 0.0)
    gray_image = roi.convert("L")
    gray_image.thumbnail((settings.damage_roi_max_side, settings.damage_roi_max_side))
    gray = np.asarray(gray_image)
    h, w = gray.shape
    yy, xx = np.ogrid[:h, :w]
    inside = (
        ((xx - (w - 1) / 2) / (w * settings.damage_inner_scale / 2)) ** 2
        + ((yy - (h - 1) / 2) / (h * settings.damage_inner_scale / 2)) ** 2
    ) <= 1
    interior_area = int(inside.sum())
    if not interior_area:
        return DarkLineResult(False, 0.0)
    cutoff = min(settings.damage_dark_threshold,
                 float(np.median(gray[inside])) - settings.damage_min_contrast)
    mask = ((gray < cutoff) & inside).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    best_area = 0.0
    for label in range(1, count):
        area_ratio = float(stats[label, cv2.CC_STAT_AREA]) / interior_area
        if area_ratio < settings.damage_min_area_ratio:
            continue
        y, x = np.where(labels == label)
        # Rotated geometry keeps diagonal lines eligible and small spots out.
        points = np.column_stack((x, y)).astype(np.float32)
        _, (side_a, side_b), _ = cv2.minAreaRect(points)
        length, thickness = max(side_a, side_b) + 1, min(side_a, side_b) + 1
        if (length / min(w, h) >= settings.damage_min_length_ratio
                and length / thickness >= settings.damage_min_elongation):
            best_area = max(best_area, area_ratio)
    return DarkLineResult(best_area > 0, round(best_area, 6))


def _box(raw: RawDetection, width: int, height: int) -> BoundingBox | None:
    coords = (raw.x1, raw.y1, raw.x2, raw.y2)
    if not all(isfinite(value) for value in coords):
        return None
    return sanitize_bbox(BoundingBox(x1=raw.x1, y1=raw.y1, x2=raw.x2, y2=raw.y2), width, height)


def analyze_eggs(image: Image.Image, detections: list[RawDetection], settings: Settings
                 ) -> tuple[list[EggResult], EggSummary]:
    width, height = image.size
    candidates = []
    for raw in detections:
        if not is_valid_egg(raw.to_detection_like(), settings.egg_confidence):
            continue
        box = _box(raw, width, height)
        if box is not None:
            candidates.append((raw, box))
    # Stable under permutations of YOLO output. IDs are local to each frame.
    candidates.sort(key=lambda pair: (
        (pair[1].x1 + pair[1].x2) / 2, (pair[1].y1 + pair[1].y2) / 2,
        pair[1].x1, pair[1].y1, pair[1].x2, pair[1].y2, -pair[0].confidence,
    ))
    cracks: list[list[Detection]] = [[] for _ in candidates]
    for raw in detections:
        if not is_valid_crack(raw.to_detection_like(), settings.crack_confidence):
            continue
        box = _box(raw, width, height)
        if box is None:
            continue
        # Assign each crack to at most one egg: center inside + greatest overlap.
        cx, cy = (box.x1 + box.x2) / 2, (box.y1 + box.y2) / 2
        owners = [(bbox_overlap_area(box, egg), index)
                  for index, (_, egg) in enumerate(candidates)
                  if egg.x1 <= cx <= egg.x2 and egg.y1 <= cy <= egg.y2]
        if owners:
            _, index = max(owners, key=lambda item: (item[0], -item[1]))
            cracks[index].append(Detection(
                class_id=raw.class_id, class_name=raw.class_name, confidence=raw.confidence,
                bbox=box, bbox_normalized=normalize_bbox(box, width, height),
                crack_source="full_frame",
            ))
    eggs = []
    for index, (raw, box) in enumerate(candidates):
        roi = image.crop((floor(box.x1), floor(box.y1), ceil(box.x2), ceil(box.y2)))
        mark = analyze_dark_line(roi, settings)
        has_crack = bool(cracks[index])
        source = ("both" if mark.detected and has_crack else "dark_line" if mark.detected
                  else "yolo_crack" if has_crack else "none")
        eggs.append(EggResult(
            id=index + 1, confidence=raw.confidence, bbox=box,
            bbox_normalized=normalize_bbox(box, width, height),
            status="damaged" if mark.detected or has_crack else "healthy",
            damage_source=source, dark_line_area_ratio=mark.area_ratio,
            cracks=sorted(cracks[index], key=lambda crack: (-crack.confidence, crack.bbox.x1, crack.bbox.y1)),
        ))
    damaged = sum(egg.status == "damaged" for egg in eggs)
    return eggs, EggSummary(total=len(eggs), healthy=len(eggs) - damaged, damaged=damaged)
