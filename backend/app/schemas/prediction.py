"""Schemas Pydantic de request/response."""

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox


class ImageInfo(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class ModelInfo(BaseModel):
    name: str
    imgsz: int


class PredictionResponse(BaseModel):
    status: str
    route: str
    reason: str
    egg_detected: bool
    crack_detected: bool
    image: ImageInfo
    detections: list[Detection]
    inference_ms: float = Field(ge=0.0)
    model: ModelInfo


class HealthResponse(BaseModel):
    status: str
    service: str
    model_loaded: bool
    model: str
    input_size: int
    model_path: str | None = None
    model_error: str | None = None


class RootResponse(BaseModel):
    name: str
    version: str
    docs: str
