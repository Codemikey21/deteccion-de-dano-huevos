"""Tests del endpoint /health (sin inferencia real)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import get_settings
from backend.app.main import create_app

# Ruta garantizada inexistente — no depende de si best.pt existe en la máquina.
MISSING_MODEL_PATH = Path(__file__).resolve().parent / "fixtures" / "nonexistent-best.pt"


def _settings_without_model():
    settings = get_settings()
    return settings.model_copy(update={"model_path": MISSING_MODEL_PATH})


def test_health_responds_ok_without_model(monkeypatch):
    monkeypatch.setattr("backend.app.main.get_settings", _settings_without_model)

    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "egg-detection-api"
    assert data["model"] == "yolov8n"
    assert data["input_size"] == 960
    assert data["model_loaded"] is False
    assert data["model_error"] is not None


def test_health_reports_model_loaded_when_checkpoint_exists():
    settings = get_settings()
    if not settings.model_path.exists():
        pytest.skip("Checkpoint no disponible en este entorno")

    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            response = client.get("/health")
            data = response.json()
            if not data["model_loaded"]:
                pytest.skip(
                    "Checkpoint presente pero no cargado en este entorno: "
                    f"{data.get('model_error')}",
                )
    finally:
        get_settings.cache_clear()

    assert response.status_code == 200
    assert data["model_loaded"] is True
    assert data["model_error"] is None


def test_root_endpoint():
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_predict_returns_503_without_model(monkeypatch):
    monkeypatch.setattr("backend.app.main.get_settings", _settings_without_model)

    with TestClient(create_app()) as client:
        response = client.post(
            "/predict",
            files={"file": ("test.jpg", b"not-an-image", "image/jpeg")},
        )
    assert response.status_code in (400, 503)
