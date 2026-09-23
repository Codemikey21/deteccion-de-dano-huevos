"""Tests de selección primary_egg y cracks asociados."""

from backend.app.schemas.prediction import BoundingBox
from backend.app.services.inference import RawDetection
from backend.app.services.primary_egg import (
    IMPOSSIBLE_AREA_RATIO,
    PRIMARY_EGG_MIN_CONFIDENCE,
    build_primary_egg_selection,
    select_primary_egg,
)


def _egg(confidence: float, x1: float, y1: float, x2: float, y2: float) -> RawDetection:
    return RawDetection(
        class_id=0,
        class_name="egg",
        confidence=confidence,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )


def _crack(confidence: float, x1: float, y1: float, x2: float, y2: float) -> RawDetection:
    return RawDetection(
        class_id=1,
        class_name="crack",
        confidence=confidence,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )


def test_egg_035_can_become_primary_egg():
    detections = [_egg(0.35, 100, 100, 300, 400)]
    primary = select_primary_egg(detections, 1000, 2000)
    assert primary is not None
    assert primary.confidence == 0.35


def test_large_egg_at_70_percent_is_not_discarded():
    detections = [_egg(0.80, 50, 50, 950, 1450)]
    primary = select_primary_egg(detections, 1000, 2000)
    assert primary is not None
    assert primary.confidence == 0.80


def test_absurd_full_frame_egg_is_rejected():
    detections = [_egg(0.95, 0, 0, 1000, 2000)]
    primary = select_primary_egg(detections, 1000, 2000)
    assert primary is None


def test_primary_egg_includes_normalized_bbox():
    detections = [_egg(0.87, 100, 200, 400, 600)]
    primary = select_primary_egg(detections, 1000, 2000)
    assert primary is not None
    assert primary.bbox_normalized.x1 == 0.1
    assert primary.bbox_normalized.y1 == 0.1
    assert primary.bbox_normalized.x2 == 0.4
    assert primary.bbox_normalized.y2 == 0.3


def test_crack_outside_egg_is_ignored():
    detections = [
        _egg(0.90, 100, 100, 300, 400),
        _crack(0.74, 900, 900, 950, 950),
    ]
    selection = build_primary_egg_selection(detections, 1000, 2000)
    assert selection.primary_egg is not None
    assert selection.associated_cracks == []


def test_crack_inside_egg_is_associated():
    detections = [
        _egg(0.78, 100, 100, 300, 400),
        _crack(0.74, 180, 220, 220, 260),
    ]
    selection = build_primary_egg_selection(detections, 1000, 2000)
    assert len(selection.associated_cracks) == 1
    assert selection.associated_cracks[0].confidence == 0.74


def test_highest_confidence_egg_wins():
    detections = [
        _egg(0.69, 100, 100, 300, 400),
        _egg(0.87, 120, 120, 320, 420),
    ]
    primary = select_primary_egg(detections, 1000, 2000)
    assert primary is not None
    assert primary.confidence == 0.87
