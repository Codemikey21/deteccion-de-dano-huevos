"""Tests de clasificación basada en primary_egg."""

from backend.app.core.constants import (
    REASON_CRACK,
    REASON_NO_CRACK,
    REASON_NO_EGG,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_UNKNOWN,
)
from backend.app.services.classification import DetectionLike, classify_primary_egg

CRACK_THRESHOLD = 0.55


def test_no_primary_egg_is_unknown():
    result = classify_primary_egg(False, [], CRACK_THRESHOLD)
    assert result.status == STATUS_UNKNOWN
    assert result.reason == REASON_NO_EGG


def test_primary_egg_without_crack_is_approved():
    result = classify_primary_egg(True, [], CRACK_THRESHOLD)
    assert result.status == STATUS_APPROVED
    assert result.reason == REASON_NO_CRACK


def test_primary_egg_with_strong_associated_crack_is_rejected():
    cracks = [DetectionLike(class_id=1, class_name="crack", confidence=0.74)]
    result = classify_primary_egg(True, cracks, CRACK_THRESHOLD)
    assert result.status == STATUS_REJECTED
    assert result.reason == REASON_CRACK


def test_weak_associated_crack_does_not_reject():
    cracks = [DetectionLike(class_id=1, class_name="crack", confidence=0.34)]
    result = classify_primary_egg(True, cracks, CRACK_THRESHOLD)
    assert result.status == STATUS_APPROVED
    assert result.crack_detected is False
