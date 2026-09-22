"""Tests unitarios de clasificación — sin YOLO."""

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
from backend.app.services.classification import DetectionLike, classify_detections


def test_egg_without_crack_is_approved():
    detections = [DetectionLike(class_id=0, class_name="egg", confidence=0.95)]
    result = classify_detections(detections, crack_confidence_threshold=0.60)
    assert result.status == STATUS_APPROVED
    assert result.route == ROUTE_ACCEPT
    assert result.reason == REASON_NO_CRACK
    assert result.egg_detected is True
    assert result.crack_detected is False


def test_egg_with_valid_crack_is_rejected():
    detections = [
        DetectionLike(class_id=0, class_name="egg", confidence=0.95),
        DetectionLike(class_id=1, class_name="crack", confidence=0.84),
    ]
    result = classify_detections(detections, crack_confidence_threshold=0.60)
    assert result.status == STATUS_REJECTED
    assert result.route == ROUTE_REJECT
    assert result.reason == REASON_CRACK
    assert result.crack_detected is True


def test_crack_without_egg_is_review():
    detections = [DetectionLike(class_id=1, class_name="crack", confidence=0.85)]
    result = classify_detections(detections, crack_confidence_threshold=0.60)
    assert result.status == STATUS_UNKNOWN
    assert result.route == ROUTE_REVIEW
    assert result.reason == REASON_CRACK_WITHOUT_EGG
    assert result.egg_detected is False
    assert result.crack_detected is True


def test_no_egg_is_unknown():
    result_empty = classify_detections([], crack_confidence_threshold=0.60)
    assert result_empty.status == STATUS_UNKNOWN
    assert result_empty.route == ROUTE_REVIEW
    assert result_empty.reason == REASON_NO_EGG

    low_crack_only = [DetectionLike(class_id=1, class_name="crack", confidence=0.10)]
    result = classify_detections(low_crack_only, crack_confidence_threshold=0.60)
    assert result.status == STATUS_UNKNOWN
    assert result.egg_detected is False


def test_crack_below_threshold_does_not_reject():
    detections = [
        DetectionLike(class_id=0, class_name="egg", confidence=0.95),
        DetectionLike(class_id=1, class_name="crack", confidence=0.10),
    ]
    result = classify_detections(detections, crack_confidence_threshold=0.60)
    assert result.status == STATUS_APPROVED
    assert result.crack_detected is False
