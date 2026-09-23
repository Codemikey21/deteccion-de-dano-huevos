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

EGG_THRESHOLD = 0.40
CRACK_THRESHOLD = 0.55


def test_egg_045_is_valid_and_approved_without_crack():
    detections = [DetectionLike(class_id=0, class_name="egg", confidence=0.45)]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_APPROVED
    assert result.egg_detected is True


def test_egg_035_is_not_valid():
    detections = [DetectionLike(class_id=0, class_name="egg", confidence=0.35)]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_UNKNOWN
    assert result.reason == REASON_NO_EGG
    assert result.egg_detected is False


def test_crack_058_with_egg_is_rejected():
    detections = [
        DetectionLike(class_id=0, class_name="egg", confidence=0.90),
        DetectionLike(class_id=1, class_name="crack", confidence=0.58),
    ]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_REJECTED
    assert result.route == ROUTE_REJECT
    assert result.reason == REASON_CRACK


def test_crack_040_with_egg_is_approved():
    detections = [
        DetectionLike(class_id=0, class_name="egg", confidence=0.90),
        DetectionLike(class_id=1, class_name="crack", confidence=0.40),
    ]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_APPROVED
    assert result.crack_detected is False


def test_crack_070_without_egg_is_review():
    detections = [DetectionLike(class_id=1, class_name="crack", confidence=0.70)]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_UNKNOWN
    assert result.route == ROUTE_REVIEW
    assert result.reason == REASON_CRACK_WITHOUT_EGG
    assert result.egg_detected is False
    assert result.crack_detected is True


def test_no_detections_is_unknown():
    result = classify_detections([], EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_UNKNOWN
    assert result.route == ROUTE_REVIEW
    assert result.reason == REASON_NO_EGG


def test_egg_without_crack_is_approved():
    detections = [DetectionLike(class_id=0, class_name="egg", confidence=0.95)]
    result = classify_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_APPROVED
    assert result.route == ROUTE_ACCEPT
    assert result.reason == REASON_NO_CRACK


def test_low_crack_only_is_unknown():
    low_crack_only = [DetectionLike(class_id=1, class_name="crack", confidence=0.31)]
    result = classify_detections(low_crack_only, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert result.status == STATUS_UNKNOWN
    assert result.egg_detected is False
    assert result.crack_detected is False
