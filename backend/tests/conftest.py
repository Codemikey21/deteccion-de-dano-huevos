"""Fixtures compartidas para tests del backend."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True)
def reset_inference_singleton():
    """Evita estado compartido del servicio YOLO entre tests."""
    from backend.app.services import inference as inference_module

    inference_module._inference_service = None
    yield
    inference_module._inference_service = None
