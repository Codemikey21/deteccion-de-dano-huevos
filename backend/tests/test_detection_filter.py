"""Tests de filtrado post-YOLO por clase."""

from backend.app.services.classification import DetectionLike
from backend.app.services.detection_filter import filter_valid_detections

EGG_THRESHOLD = 0.40
CRACK_THRESHOLD = 0.55


def test_filter_keeps_valid_egg_and_crack():
    detections = [
        DetectionLike(class_id=0, class_name="egg", confidence=0.45),
        DetectionLike(class_id=1, class_name="crack", confidence=0.58),
        DetectionLike(class_id=1, class_name="crack", confidence=0.31),
    ]
    filtered = filter_valid_detections(detections, EGG_THRESHOLD, CRACK_THRESHOLD)
    assert len(filtered) == 2
    assert filtered[0].class_name == "egg"
    assert filtered[1].confidence == 0.58
