"""Regression tests for missing brown eggs and illumination false positives."""
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageEnhance

from backend.app.core.config import Settings
from backend.app.schemas.prediction import BoundingBox
from backend.app.services.demo_localization import EggCandidate, find_demo_eggs, merge_candidates
from backend.app.services.multi_egg import analyze_dark_line, analyze_eggs
from backend.app.services.inference import RawDetection
from backend.tests.test_multi_egg import endpoint_client, post_image

FIXTURES = Path(__file__).parent / "fixtures" / "demo_regression"
COUNTS = [4, 1, 1, 2, 2, 2, 4, 4, 4]


@pytest.fixture
def settings():
    # Freeze the demo defaults; tests must not depend on the operator's .env.
    return Settings(_env_file=None, enable_multi_egg=True, enable_demo_localization=True,
                    demo_min_saturation=65, demo_min_value=65, demo_min_area_ratio=0.003,
                    demo_max_area_ratio=0.45, demo_max_side=640, demo_max_objects=32,
                    egg_confidence=0.4, crack_confidence=0.55,
                    damage_dark_threshold=100, damage_min_contrast=35,
                    damage_min_area_ratio=0.003, damage_min_length_ratio=0.18,
                    damage_min_elongation=2.5, damage_inner_scale=0.8,
                    damage_roi_max_side=256, damage_local_window_ratio=0.25,
                    damage_mark_area_ratio=0.015)


@pytest.mark.parametrize("scene", range(1, 10))
@pytest.mark.parametrize("variant", ["original", "smaller", "dimmer", "brighter"])
def test_screenshot_objects_without_any_yolo_eggs(settings, scene, variant):
    image = Image.open(FIXTURES / f"scene-{scene}.png").convert("RGB")
    if variant == "smaller":
        image = image.resize((int(image.width * 0.65), int(image.height * 0.65)))
    elif variant in ("dimmer", "brighter"):
        image = ImageEnhance.Brightness(image).enhance(0.8 if variant == "dimmer" else 1.2)
    eggs, summary = analyze_eggs(image, [], settings)
    assert summary.total == COUNTS[scene-1]
    # Marker cases: one damaged egg, no false damage on the other eggs/shadows.
    if scene in (1, 2, 3, 7, 8, 9):
        assert summary.damaged == 1
        assert summary.healthy == summary.total-1
    else:
        # Pale physical breaks require the model; do not fabricate dark marks.
        assert summary.damaged == 0
    assert all(egg.localization_source == "demo_shape" and egg.confidence == 0 for egg in eggs)


@pytest.mark.parametrize("scene,box", [
    (4, (302, 166, 347, 216)), (5, (307, 197, 357, 264)), (6, (355, 220, 400, 272)),
])
def test_visible_break_associated_to_only_correct_egg(settings, scene, box):
    image = Image.open(FIXTURES / f"scene-{scene}.png").convert("RGB")
    # Full-frame crack boxes observed with the existing checkpoint.
    crack = RawDetection(1, "crack", 0.8, *box)
    eggs, summary = analyze_eggs(image, [crack], settings)
    assert summary.model_dump() == dict(total=2, healthy=1, damaged=1)
    assert [egg.status for egg in eggs] == ["healthy", "damaged"]
    assert eggs[1].damage_source == "yolo_crack"


def test_endpoint_recovers_four_eggs_without_extra_model_calls(monkeypatch, settings):
    image = Image.open(FIXTURES / "scene-7.png").convert("RGB")
    client, inference = endpoint_client(monkeypatch, settings, image, [])
    response = post_image(client, image)
    assert response.status_code == 200
    assert response.json()["summary"] == dict(total=4, healthy=3, damaged=1)
    assert inference.full_calls == 1 and inference.roi_calls == 0
    assert {egg["localization_source"] for egg in response.json()["eggs"]} == {"demo_shape"}


def test_localization_can_be_disabled(settings):
    image = Image.open(FIXTURES / "scene-7.png").convert("RGB")
    assert analyze_eggs(image, [], settings.model_copy(update={"enable_demo_localization": False}))[1].total == 0


@pytest.mark.parametrize("kind", ["gray", "brown", "rectangle", "line", "edge", "noise"])
def test_no_hallucinated_eggs_on_backgrounds(settings, kind):
    image = Image.new("RGB", (400, 300), "#888888" if kind != "brown" else "#b47b39")
    draw = ImageDraw.Draw(image)
    if kind == "rectangle":
        draw.rectangle((80, 80, 230, 220), fill="#b47b39")
    elif kind == "line":
        draw.line((40, 100, 350, 130), fill="#b47b39", width=10)
    elif kind == "edge":
        draw.ellipse((-50, 60, 70, 220), fill="#b47b39")
    elif kind == "noise":
        for x in range(5, 400, 20):
            for y in range(5, 300, 20):
                draw.ellipse((x, y, x+3, y+3), fill="#b47b39")
    assert find_demo_eggs(image, settings) == []


def test_five_synthetic_eggs_and_bounds(settings):
    image = Image.new("RGB", (850, 240), "#888888")
    draw = ImageDraw.Draw(image)
    for x in range(20, 820, 170):
        draw.ellipse((x, 40, x+110, 200), fill="#b47b39")
    eggs, summary = analyze_eggs(image, [], settings)
    assert summary.total == summary.healthy == 5
    assert [egg.id for egg in eggs] == [1, 2, 3, 4, 5]
    assert all(0 < e.bbox_normalized.x1 < e.bbox_normalized.x2 < 1 for e in eggs)


def box(x1, y1, x2, y2):
    return BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)


def test_fallback_and_yolo_are_not_double_counted():
    shapes = [box(10, 10, 100, 130), box(110, 10, 200, 130)]
    yolo = [EggCandidate(box(8, 8, 101, 132), 0.9), EggCandidate(box(10, 10, 100, 130), 0.8)]
    result = merge_candidates(yolo, shapes)
    assert len(result) == 2
    assert result[0].confidence == 0.9 and result[0].localization_source == "yolo+demo_shape"
    assert result[1].confidence == 0


def test_group_box_is_replaced_by_separate_shapes():
    shapes = [box(10, 10, 100, 130), box(110, 10, 200, 130)]
    result = merge_candidates([EggCandidate(box(0, 0, 210, 140), 0.9)], shapes)
    assert len(result) == 2
    assert all(candidate.confidence == 0 for candidate in result)


def test_unmatched_yolo_detection_is_preserved():
    yolo = EggCandidate(box(210, 10, 300, 130), 0.9)
    result = merge_candidates([yolo], [box(10, 10, 100, 130)])
    assert yolo in result and len(result) == 2


def test_smooth_dark_hemisphere_is_not_damage(settings):
    # Shading goes far below the absolute dark cutoff but varies smoothly.
    pixels = np.tile(np.linspace(230, 20, 150).astype(np.uint8)[:, None], (1, 120))
    image = Image.fromarray(pixels)
    assert not analyze_dark_line(image, settings).detected
    marked = image.convert("RGB")
    ImageDraw.Draw(marked).line((30, 50, 85, 80), fill="black", width=3)
    assert analyze_dark_line(marked, settings).detected
