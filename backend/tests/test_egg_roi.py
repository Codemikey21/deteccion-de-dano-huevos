"""Tests de la segunda etapa de inferencia (ROI alrededor del primary_egg)."""

from PIL import Image

from backend.app.core.constants import STATUS_APPROVED, STATUS_REJECTED
from backend.app.schemas.prediction import BoundingBox, Detection, NormalizedBBox, PrimaryEgg
from backend.app.services.classification import DetectionLike, classify_primary_egg
from backend.app.services.egg_roi import (
    SOURCE_BOTH,
    SOURCE_EGG_ROI,
    SOURCE_FULL_FRAME,
    compute_roi_bbox,
    crop_roi,
    extract_roi_cracks,
    merge_crack_detections,
    run_egg_roi_crack_pass,
)
from backend.app.services.inference import InferenceOutput, RawDetection

IMAGE_WIDTH = 1000
IMAGE_HEIGHT = 2000
CRACK_THRESHOLD = 0.55


def _egg_bbox(x1: float, y1: float, x2: float, y2: float) -> BoundingBox:
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def _primary_egg(bbox: BoundingBox, confidence: float = 0.85) -> PrimaryEgg:
    return PrimaryEgg(
        confidence=confidence,
        bbox=bbox,
        bbox_normalized=NormalizedBBox(
            x1=bbox.x1 / IMAGE_WIDTH,
            y1=bbox.y1 / IMAGE_HEIGHT,
            x2=bbox.x2 / IMAGE_WIDTH,
            y2=bbox.y2 / IMAGE_HEIGHT,
        ),
    )


def _crack_detection(x1: float, y1: float, x2: float, y2: float, confidence: float) -> Detection:
    bbox = BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
    return Detection(
        class_id=1,
        class_name="crack",
        confidence=confidence,
        bbox=bbox,
        bbox_normalized=NormalizedBBox(
            x1=bbox.x1 / IMAGE_WIDTH,
            y1=bbox.y1 / IMAGE_HEIGHT,
            x2=bbox.x2 / IMAGE_WIDTH,
            y2=bbox.y2 / IMAGE_HEIGHT,
        ),
    )


def _fake_runner(output: InferenceOutput):
    calls: list[Image.Image] = []

    def run(image: Image.Image, confidence: float, imgsz: int) -> InferenceOutput:
        calls.append(image)
        return output

    return run, calls


# --- 1. padding correcto -----------------------------------------------------


def test_compute_roi_bbox_applies_symmetric_padding():
    egg_bbox = _egg_bbox(100, 100, 300, 400)  # width=200, height=300
    roi = compute_roi_bbox(egg_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, padding_ratio=0.10)

    assert roi.x1 == 80.0
    assert roi.y1 == 70.0
    assert roi.x2 == 320.0
    assert roi.y2 == 430.0


# --- 2. clamp correcto --------------------------------------------------------


def test_compute_roi_bbox_clamps_to_image_bounds():
    egg_bbox = _egg_bbox(5, 5, 60, 80)
    roi = compute_roi_bbox(egg_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, padding_ratio=0.5)

    assert roi.x1 == 0.0
    assert roi.y1 == 0.0
    assert roi.x2 <= IMAGE_WIDTH
    assert roi.y2 <= IMAGE_HEIGHT


def test_compute_roi_bbox_clamps_near_far_edge():
    egg_bbox = _egg_bbox(950, 1950, 995, 1995)
    roi = compute_roi_bbox(egg_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, padding_ratio=0.5)

    assert roi.x2 == float(IMAGE_WIDTH)
    assert roi.y2 == float(IMAGE_HEIGHT)


# --- 3. crop correcto ---------------------------------------------------------


def test_crop_roi_returns_expected_size():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    roi_bbox = BoundingBox(x1=80, y1=70, x2=320, y2=430)

    cropped = crop_roi(image, roi_bbox)

    assert cropped is not None
    assert cropped.size == (240, 360)


def test_crop_roi_returns_none_for_degenerate_bbox():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    roi_bbox = BoundingBox(x1=100, y1=100, x2=100.5, y2=101)

    assert crop_roi(image, roi_bbox) is None


# --- 4. remap crop -> original -------------------------------------------------


def test_extract_roi_cracks_remaps_to_original_coordinates():
    roi_bbox = BoundingBox(x1=80, y1=70, x2=320, y2=430)
    roi_detections = [
        RawDetection(class_id=1, class_name="crack", confidence=0.60, x1=10, y1=20, x2=50, y2=80),
    ]

    cracks = extract_roi_cracks(roi_detections, roi_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, min_confidence=0.25)

    assert len(cracks) == 1
    crack = cracks[0]
    assert crack.bbox.x1 == 90.0
    assert crack.bbox.y1 == 90.0
    assert crack.bbox.x2 == 130.0
    assert crack.bbox.y2 == 150.0
    assert crack.crack_source == SOURCE_EGG_ROI


def test_extract_roi_cracks_ignores_egg_class():
    roi_bbox = BoundingBox(x1=80, y1=70, x2=320, y2=430)
    roi_detections = [
        RawDetection(class_id=0, class_name="egg", confidence=0.90, x1=0, y1=0, x2=200, y2=300),
    ]

    cracks = extract_roi_cracks(roi_detections, roi_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, min_confidence=0.25)

    assert cracks == []


def test_extract_roi_cracks_filters_below_min_confidence():
    roi_bbox = BoundingBox(x1=80, y1=70, x2=320, y2=430)
    roi_detections = [
        RawDetection(class_id=1, class_name="crack", confidence=0.20, x1=10, y1=20, x2=50, y2=80),
    ]

    cracks = extract_roi_cracks(roi_detections, roi_bbox, IMAGE_WIDTH, IMAGE_HEIGHT, min_confidence=0.25)

    assert cracks == []


# --- 5. sin egg => no segundo pase ---------------------------------------------


def test_run_egg_roi_crack_pass_skips_second_stage_without_primary_egg():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    output = InferenceOutput(detections=[], width=1, height=1, inference_ms=5.0, image=image)
    runner, calls = _fake_runner(output)

    result = run_egg_roi_crack_pass(
        image=image,
        primary_egg=None,
        full_frame_associated_cracks=[],
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        padding_ratio=0.12,
        min_confidence=0.25,
        imgsz=960,
        enabled=True,
        run_inference=runner,
    )

    assert result.roi_used is False
    assert result.roi_cracks == []
    assert calls == []


def test_run_egg_roi_crack_pass_skips_when_disabled_by_flag():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    primary_egg = _primary_egg(_egg_bbox(100, 100, 300, 400))
    output = InferenceOutput(detections=[], width=1, height=1, inference_ms=5.0, image=image)
    runner, calls = _fake_runner(output)

    result = run_egg_roi_crack_pass(
        image=image,
        primary_egg=primary_egg,
        full_frame_associated_cracks=[],
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        padding_ratio=0.12,
        min_confidence=0.25,
        imgsz=960,
        enabled=False,
        run_inference=runner,
    )

    assert result.roi_used is False
    assert calls == []


# --- crack ROI => asociado a primary egg --------------------------------------


def test_run_egg_roi_crack_pass_associates_roi_crack_to_primary_egg():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    primary_egg = _primary_egg(_egg_bbox(100, 100, 300, 400))

    roi_detections = [
        RawDetection(class_id=1, class_name="crack", confidence=0.60, x1=10, y1=20, x2=50, y2=80),
    ]
    output = InferenceOutput(detections=roi_detections, width=1, height=1, inference_ms=12.0, image=image)
    runner, calls = _fake_runner(output)

    result = run_egg_roi_crack_pass(
        image=image,
        primary_egg=primary_egg,
        full_frame_associated_cracks=[],
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        padding_ratio=0.10,
        min_confidence=0.25,
        imgsz=960,
        enabled=True,
        run_inference=runner,
    )

    assert len(calls) == 1
    assert result.roi_used is True
    assert len(result.associated_cracks) == 1
    assert result.associated_cracks[0].crack_source == SOURCE_EGG_ROI
    assert result.best_roi_crack_confidence == 0.60
    assert result.roi_inference_ms == 12.0


# --- duplicados full-frame/ROI => deduplicados --------------------------------


def test_merge_crack_detections_deduplicates_overlapping_boxes():
    full_frame = [_crack_detection(180, 220, 220, 260, confidence=0.50)]
    roi = [_crack_detection(182, 221, 219, 259, confidence=0.65)]

    merged = merge_crack_detections(full_frame, roi)

    assert len(merged) == 1
    assert merged[0].confidence == 0.65
    assert merged[0].crack_source == SOURCE_BOTH


def test_merge_crack_detections_keeps_distinct_boxes_separate():
    full_frame = [_crack_detection(180, 220, 220, 260, confidence=0.50)]
    roi = [_crack_detection(900, 900, 950, 950, confidence=0.40)]

    merged = merge_crack_detections(full_frame, roi)

    assert len(merged) == 2
    sources = {detection.crack_source for detection in merged}
    assert sources == {SOURCE_FULL_FRAME, SOURCE_EGG_ROI}


# --- strong ROI => influye en clasificación -----------------------------------


def test_strong_roi_only_crack_flips_classification_to_rejected():
    """Caso del bug reportado: grieta visible pero invisible en full-frame,
    resuelta al inferir de nuevo sobre el recorte ROI a mayor resolución."""
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    primary_egg = _primary_egg(_egg_bbox(100, 100, 300, 400))

    roi_detections = [
        RawDetection(class_id=1, class_name="crack", confidence=0.60, x1=10, y1=20, x2=50, y2=80),
    ]
    output = InferenceOutput(detections=roi_detections, width=1, height=1, inference_ms=12.0, image=image)
    runner, _ = _fake_runner(output)

    result = run_egg_roi_crack_pass(
        image=image,
        primary_egg=primary_egg,
        full_frame_associated_cracks=[],  # nada visto en full-frame
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        padding_ratio=0.10,
        min_confidence=0.25,
        imgsz=960,
        enabled=True,
        run_inference=runner,
    )

    associated_crack_likes = [
        DetectionLike(class_id=c.class_id, class_name=c.class_name, confidence=c.confidence)
        for c in result.associated_cracks
    ]
    classification = classify_primary_egg(
        has_primary_egg=True,
        associated_cracks=associated_crack_likes,
        crack_confidence_threshold=CRACK_THRESHOLD,
    )

    assert classification.status == STATUS_REJECTED
    assert classification.crack_detected is True


# --- weak repetido => temporal puede rechazar ---------------------------------


def test_weak_roi_crack_is_surfaced_as_evidence_for_frontend_temporal_window():
    """Una grieta 'weak' (0.30-0.55) hallada solo en ROI no rechaza por sí sola
    en un único frame, pero debe llegar íntegra en `cracks` para que la ventana
    temporal del frontend (mobile/src/utils/crackEvidence.ts, sin cambios) la
    pueda acumular y rechazar tras varios frames repetidos."""
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))
    primary_egg = _primary_egg(_egg_bbox(100, 100, 300, 400))

    roi_detections = [
        RawDetection(class_id=1, class_name="crack", confidence=0.35, x1=10, y1=20, x2=50, y2=80),
    ]
    output = InferenceOutput(detections=roi_detections, width=1, height=1, inference_ms=12.0, image=image)
    runner, _ = _fake_runner(output)

    result = run_egg_roi_crack_pass(
        image=image,
        primary_egg=primary_egg,
        full_frame_associated_cracks=[],
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        padding_ratio=0.10,
        min_confidence=0.25,
        imgsz=960,
        enabled=True,
        run_inference=runner,
    )

    assert len(result.associated_cracks) == 1
    assert result.associated_cracks[0].confidence == 0.35
    assert result.associated_cracks[0].crack_source == SOURCE_EGG_ROI

    associated_crack_likes = [
        DetectionLike(class_id=c.class_id, class_name=c.class_name, confidence=c.confidence)
        for c in result.associated_cracks
    ]
    classification = classify_primary_egg(
        has_primary_egg=True,
        associated_cracks=associated_crack_likes,
        crack_confidence_threshold=CRACK_THRESHOLD,
    )

    # Un solo frame con evidencia weak no rechaza todavía (regla temporal
    # vive en el frontend); pero la evidencia quedó disponible para acumularse.
    assert classification.status == STATUS_APPROVED
