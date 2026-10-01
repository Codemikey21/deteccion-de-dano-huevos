"""Conservative brown-egg localization for a neutral-background demonstration.

This is a configurable color/shape heuristic, not a trained egg detector. It
complements the single YOLO pass and does not assign invented model confidence.
"""
from dataclasses import dataclass
from math import pi, sqrt

import cv2
import numpy as np
from PIL import Image

from backend.app.core.config import Settings
from backend.app.schemas.prediction import BoundingBox
from backend.app.services.bbox_utils import bbox_iou, bbox_overlap_area


@dataclass(frozen=True)
class EggCandidate:
    bbox: BoundingBox
    confidence: float
    localization_source: str = "yolo"


def find_demo_eggs(image: Image.Image, settings: Settings) -> list[BoundingBox]:
    if not settings.enable_demo_localization:
        return []
    small = image.convert("RGB")
    scale = settings.demo_max_side / max(image.size)
    small = small.resize((max(1, round(image.width*scale)), max(1, round(image.height*scale))),
                         Image.Resampling.BILINEAR)
    rgb = np.asarray(small)
    height, width = rgb.shape[:2]
    if min(width, height) < 24:
        return []
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    brown = ((hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 38)
             & (hsv[:, :, 1] >= settings.demo_min_saturation))
    if not brown.any():
        return []
    exposure = np.clip(float(np.percentile(hsv[:, :, 2][brown], 90)) / 200, 0.5, 1.4)
    mask = (brown & (hsv[:, :, 2] >= settings.demo_min_value * exposure)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE,
                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, contours, -1, 255, -1)
    count, components, stats, _ = cv2.connectedComponentsWithStats(filled)
    min_area = width * height * settings.demo_min_area_ratio
    max_area = width * height * settings.demo_max_area_ratio
    peak_window = max(9, int(min(width, height) * 0.06) | 1)
    boxes = []
    for component in range(1, count):
        if stats[component, cv2.CC_STAT_AREA] < min_area:
            continue
        x0, y0, cw, ch = stats[component, :4]
        region = (components[y0:y0+ch, x0:x0+cw] == component).astype(np.uint8)
        # Padding ensures distanceToBackground is defined even for solid crops.
        region = np.pad(region, 1)
        distance = cv2.distanceTransform(region, cv2.DIST_L2, 5)
        peaks = ((distance == cv2.dilate(distance, np.ones((peak_window, peak_window), np.uint8)))
                 & (distance >= max(6, sqrt(min_area / pi) * 0.5))).astype(np.uint8)
        n, _, _, centers = cv2.connectedComponentsWithStats(peaks)
        possible = [(round(x), round(y), float(distance[round(y), round(x)]))
                    for x, y in centers[1:n]]
        seeds = []
        for x, y, radius in sorted(possible, key=lambda p: (-p[2], p[0], p[1])):
            if not any(np.hypot(x-a, y-b) < 0.65 * (radius+r) for a, b, r in seeds):
                seeds.append((x, y, radius))
        if not seeds or len(seeds) > settings.demo_max_objects:
            continue
        yy, xx = np.indices(region.shape)
        nearest = np.full(region.shape, np.inf)
        labels = np.zeros(region.shape, dtype=np.int32)
        # Geometry rather than RGB watershed avoids splitting on shell texture.
        for index, (x, y, _) in enumerate(seeds, 1):
            score = (xx-x)**2 + (yy-y)**2
            update = score < nearest
            labels[update] = index
            nearest[update] = score[update]
        for index in range(1, len(seeds)+1):
            part = ((labels == index) & (region > 0)).astype(np.uint8)
            pieces, _ = cv2.findContours(part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not pieces:
                continue
            contour = max(pieces, key=cv2.contourArea)
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            hull_area = cv2.contourArea(cv2.convexHull(contour))
            if not (min_area <= area <= max_area):
                continue
            if min(w, h) / max(w, h) < 0.45 or not 0.50 <= area / (w*h) <= 0.92:
                continue
            if area / max(hull_area, 1) < 0.80:
                continue
            x, y = int(x+x0-1), int(y+y0-1)
            # Partial objects at the image edge are not a safe fallback candidate.
            if x <= 1 or y <= 1 or x+w >= width-1 or y+h >= height-1:
                continue
            sx, sy = image.width / width, image.height / height
            boxes.append(BoundingBox(x1=x*sx, y1=y*sy, x2=(x+w)*sx, y2=(y+h)*sy))
    return sorted(boxes, key=lambda b: (b.x1, b.y1))[:settings.demo_max_objects]


def _area(box: BoundingBox) -> float:
    return (box.x2-box.x1) * (box.y2-box.y1)


def merge_candidates(yolo: list[EggCandidate], shapes: list[BoundingBox]) -> list[EggCandidate]:
    """Refine matched crops; never count the same object from both sources.

    One overly broad YOLO box can cover several shape candidates. In that case
    use the individually localized shapes, without duplicating its confidence.
    """
    if not shapes:
        return yolo
    result = [EggCandidate(box, 0.0, "demo_shape") for box in shapes]
    for candidate in sorted(yolo, key=lambda c: -c.confidence):
        matches = [i for i, box in enumerate(shapes)
                   if bbox_iou(candidate.bbox, box) >= 0.25
                   or bbox_overlap_area(candidate.bbox, box) / max(_area(box), 1) >= 0.65]
        if len(matches) == 1:
            i = matches[0]
            if candidate.confidence > result[i].confidence:
                result[i] = EggCandidate(shapes[i], candidate.confidence, "yolo+demo_shape")
        elif not matches:
            if not any(bbox_iou(candidate.bbox, existing.bbox) > 0.5 for existing in result):
                result.append(candidate)
    return result
