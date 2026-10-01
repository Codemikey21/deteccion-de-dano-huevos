"""Synthetic image and endpoint tests; no checkpoint/training required."""
import importlib
import io

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.app.core.config import Settings
from backend.app.services.inference import InferenceOutput, RawDetection
from backend.app.services.multi_egg import analyze_dark_line, analyze_eggs


@pytest.fixture
def settings():
    return Settings(_env_file=None, enable_multi_egg=True, egg_confidence=0.4,
                    crack_confidence=0.55, damage_dark_threshold=100,
                    damage_min_contrast=35, damage_min_area_ratio=0.003,
                    damage_min_length_ratio=0.18, damage_min_elongation=2.5,
                    damage_inner_scale=0.8, damage_roi_max_side=256)


def detection(box, confidence=0.9, crack=False):
    return RawDetection(1 if crack else 0, "crack" if crack else "egg", confidence, *box)


def scene(count, damaged=()):
    image = Image.new("RGB", (max(count, 1) * 140, 160), "#333333")
    draw = ImageDraw.Draw(image)
    detections = []
    for index in range(count):
        x = index * 140 + 10
        box = (x, 20, x + 120, 140)
        draw.ellipse(box, fill="white")
        if index in damaged:
            draw.line((x + 35, 55, x + 80, 100), fill="black", width=4)
        detections.append(detection(box))
    return image, detections


@pytest.mark.parametrize("count,damaged", [(0, ()), (1, ()), (1, (0,)), (5, (1, 3))])
def test_counts_status_and_order(settings, count, damaged):
    image, detections = scene(count, damaged)
    eggs, summary = analyze_eggs(image, list(reversed(detections)), settings)
    assert summary.model_dump() == dict(total=count, healthy=count-len(damaged), damaged=len(damaged))
    assert [egg.id for egg in eggs] == list(range(1, count+1))
    assert [egg.status for egg in eggs] == ["damaged" if i in damaged else "healthy" for i in range(count)]
    assert [egg.damage_source for egg in eggs] == ["dark_line" if i in damaged else "none" for i in range(count)]
    assert [egg.bbox.x1 for egg in eggs] == sorted(egg.bbox.x1 for egg in eggs)
    assert analyze_eggs(image, detections, settings) == (eggs, summary)


@pytest.mark.parametrize("line", [(35, 60, 85, 60), (60, 35, 60, 85), (35, 35, 85, 85)])
def test_dark_line_orientations(settings, line):
    image = Image.new("RGB", (120, 120), "white")
    ImageDraw.Draw(image).line(line, fill="black", width=3)
    assert analyze_dark_line(image, settings).detected


@pytest.mark.parametrize("kind", ["plain", "brown", "dark", "corner", "spot", "noise", "gradient", "tiny"])
def test_non_damage(settings, kind):
    image = Image.new("RGB", (120, 120), {"brown": "#765432", "dark": "#151515"}.get(kind, "white"))
    draw = ImageDraw.Draw(image)
    if kind == "corner":
        draw.rectangle((0, 0, 10, 119), fill="black")
    if kind == "spot":
        draw.ellipse((55, 55, 65, 65), fill="black")
    if kind == "noise":
        for x in range(20, 100, 8):
            draw.point((x, 60), fill="black")
    if kind == "gradient":
        image = Image.fromarray(np.tile(np.linspace(110, 255, 120).astype(np.uint8), (120, 1)))
    if kind == "tiny":
        image = image.resize((6, 6))
    assert not analyze_dark_line(image, settings).detected


def test_threshold_is_configurable(settings):
    image = Image.new("RGB", (120, 120), "white")
    ImageDraw.Draw(image).line((35, 60, 85, 60), fill=(120, 120, 120), width=3)
    assert not analyze_dark_line(image, settings).detected
    assert analyze_dark_line(image, settings.model_copy(update={"damage_dark_threshold": 150})).detected


def test_yolo_crack_assigned_only_to_its_egg(settings):
    image, detections = scene(2)
    detections += [detection((185, 55, 220, 75), crack=True),
                   detection((130, 1, 139, 10), crack=True)]
    eggs, summary = analyze_eggs(image, detections, settings)
    assert [egg.status for egg in eggs] == ["healthy", "damaged"]
    assert eggs[1].damage_source == "yolo_crack"
    assert len(eggs[1].cracks) == 1
    assert summary.damaged == 1


def test_overlapping_eggs_do_not_share_crack(settings):
    image = Image.new("RGB", (250, 150), "white")
    detections = [detection((10, 10, 150, 140)), detection((100, 10, 240, 140)),
                  detection((110, 50, 130, 80), crack=True)]
    eggs, summary = analyze_eggs(image, detections, settings)
    assert sum(len(egg.cracks) for egg in eggs) == 1
    assert summary.damaged == 1


def test_both_sources_and_weak_crack(settings):
    image, detections = scene(2, (0,))
    detections += [detection((45, 55, 85, 100), crack=True),
                   detection((185, 55, 220, 100), confidence=0.3, crack=True)]
    eggs, _ = analyze_eggs(image, detections, settings)
    assert [egg.damage_source for egg in eggs] == ["both", "none"]


def test_invalid_boxes_and_confidence(settings):
    image = Image.new("RGB", (100, 100), "white")
    detections = [detection((10, 10, 50, 50), 0.2), detection((110, 110, 120, 120)),
                  detection((10, 10, 10, 20)), detection((-10, -10, 50, 50))]
    eggs, summary = analyze_eggs(image, detections, settings)
    assert summary.total == 1
    assert eggs[0].bbox.x1 == eggs[0].bbox.y1 == 0
    assert eggs[0].bbox_normalized.x2 == 0.5


def endpoint_client(monkeypatch, settings, image, detections):
    module = importlib.import_module("backend.app.api.routes.predict")

    class FakeInference:
        is_loaded = True
        full_calls = 0
        roi_calls = 0

        def predict(self, **kwargs):
            self.full_calls += 1
            assert kwargs["imgsz"] == 960
            return InferenceOutput(detections, *image.size, 10.0, image)

        def predict_image(self, roi, **kwargs):
            self.roi_calls += 1
            return InferenceOutput([], *roi.size, 5.0, roi)

    inference = FakeInference()
    monkeypatch.setattr(module, "get_settings", lambda: settings)
    monkeypatch.setattr(module, "get_inference_service", lambda: inference)
    app = FastAPI()
    app.include_router(module.router)
    return TestClient(app), inference


def post_image(client, image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return client.post("/predict", files={"file": ("scene.png", buffer.getvalue(), "image/png")})


@pytest.mark.parametrize("count,damaged", [(0, ()), (1, ()), (1, (0,)), (5, (1, 3))])
def test_endpoint_one_model_pass(monkeypatch, settings, count, damaged):
    image, detections = scene(count, damaged)
    client, inference = endpoint_client(monkeypatch, settings, image, detections)
    response = post_image(client, image)
    assert response.status_code == 200, response.text
    body = response.json()
    assert inference.full_calls == 1
    assert inference.roi_calls == 0
    assert body["summary"] == dict(total=count, healthy=count-len(damaged), damaged=len(damaged))
    assert len(body["eggs"]) == count
    assert body["roi_used"] is False
    assert body["timing"]["full_frame_ms"] == body["inference_ms"] == 10
    assert body["timing"]["total_ms"] >= body["timing"]["roi_analysis_ms"] >= 0
    assert body["egg_detected"] == (count > 0)
    assert body["status"] == ("unknown" if count == 0 else "rejected" if 0 in damaged else "approved")
    assert bool(body["primary_egg"]) == (count > 0)


def test_legacy_flag_restores_roi_pass(monkeypatch, settings):
    image, detections = scene(1)
    legacy = settings.model_copy(update={"enable_multi_egg": False, "enable_egg_roi_inference": True})
    client, inference = endpoint_client(monkeypatch, legacy, image, detections)
    response = post_image(client, image)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["eggs"] is None and body["summary"] is None
    assert body["status"] == "approved"
    assert body["roi_used"] is True
    assert inference.full_calls == inference.roi_calls == 1
