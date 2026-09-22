"""Tests del endpoint /health (sin inferencia real)."""

from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_responds_ok_without_model():
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


def test_root_endpoint():
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_predict_returns_503_without_model():
    with TestClient(create_app()) as client:
        response = client.post(
            "/predict",
            files={"file": ("test.jpg", b"not-an-image", "image/jpeg")},
        )
    assert response.status_code in (400, 503)
