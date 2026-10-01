"""Schemas Pydantic de request/response."""

from typing import Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class NormalizedBBox(BaseModel):
    x1: float = Field(ge=0.0, le=1.0)
    y1: float = Field(ge=0.0, le=1.0)
    x2: float = Field(ge=0.0, le=1.0)
    y2: float = Field(ge=0.0, le=1.0)


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    bbox_normalized: NormalizedBBox | None = None
    # Origen del crack tras combinar full-frame + ROI: "full_frame" | "egg_roi" | "both".
    crack_source: str | None = None


class PrimaryEgg(BaseModel):
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    bbox_normalized: NormalizedBBox


class ImageInfo(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class ModelInfo(BaseModel):
    name: str
    imgsz: int


class EggResult(PrimaryEgg):
    # Frame-local number; not a persistent tracking identity.
    id: int = Field(ge=1)
    status: Literal["healthy", "damaged"]
    damage_source: Literal["none", "dark_line", "yolo_crack", "both"]
    dark_line_area_ratio: float = Field(ge=0.0, le=1.0)
    cracks: list[Detection] = Field(default_factory=list)


class EggSummary(BaseModel):
    total: int = Field(ge=0)
    healthy: int = Field(ge=0)
    damaged: int = Field(ge=0)


class PredictionTiming(BaseModel):
    full_frame_ms: float = Field(ge=0.0)
    roi_analysis_ms: float = Field(ge=0.0)
    total_ms: float = Field(ge=0.0)


class PredictionResponse(BaseModel):
    # None means legacy mode; [] means multi-egg mode found no eggs.
    eggs: list[EggResult] | None = None
    summary: EggSummary | None = None
    timing: PredictionTiming | None = None
    status: str
    route: str
    reason: str
    egg_detected: bool
    crack_detected: bool
    image: ImageInfo
    primary_egg: PrimaryEgg | None = None
    cracks: list[Detection] = Field(default_factory=list)
    raw_detections: list[Detection]
    detections: list[Detection]
    inference_ms: float = Field(ge=0.0)
    model: ModelInfo

    # Diagnóstico de la segunda etapa (ROI) — no consumido por la UI final.
    roi_used: bool = False
    roi_bbox: BoundingBox | None = None
    roi_cracks: list[Detection] = Field(default_factory=list)
    best_roi_crack_confidence: float | None = None
    crack_source: str | None = None
    full_frame_inference_ms: float | None = None
    roi_inference_ms: float | None = None
    total_inference_ms: float | None = None


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
