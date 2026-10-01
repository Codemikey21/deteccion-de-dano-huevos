"""Configuración vía variables de entorno."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Settings cargadas desde entorno y opcionalmente backend/.env."""

    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model_path: Path = Field(default=REPO_ROOT / "backend" / "models" / "best.pt")
    model_confidence: float = Field(default=0.25, ge=0.0, le=1.0)
    egg_confidence: float = Field(default=0.40, ge=0.0, le=1.0)
    crack_confidence: float = Field(default=0.55, ge=0.0, le=1.0)
    cors_origins: str = Field(default="*")

    # Demo: a single full-frame YOLO pass plus inexpensive per-egg analysis.
    enable_multi_egg: bool = True
    # Brown/ochre demo objects on a neutral background. Disable for general use.
    enable_demo_localization: bool = True
    demo_min_saturation: int = Field(default=65, ge=0, le=255)
    demo_min_value: int = Field(default=65, ge=0, le=255)
    demo_min_area_ratio: float = Field(default=0.003, gt=0.0, le=0.1)
    demo_max_area_ratio: float = Field(default=0.45, gt=0.1, le=1.0)
    demo_max_side: int = Field(default=640, ge=128, le=1280)
    demo_max_objects: int = Field(default=32, ge=1, le=64)
    damage_local_window_ratio: float = Field(default=0.25, gt=0.0, le=0.75)
    damage_mark_area_ratio: float = Field(default=0.015, gt=0.0, le=1.0)
    damage_dark_threshold: int = Field(default=100, ge=0, le=255)
    damage_min_contrast: int = Field(default=35, ge=1, le=255)
    damage_min_area_ratio: float = Field(default=0.003, gt=0.0, le=1.0)
    damage_min_length_ratio: float = Field(default=0.18, gt=0.0, le=1.0)
    damage_min_elongation: float = Field(default=2.5, ge=1.0)
    damage_inner_scale: float = Field(default=0.80, gt=0.0, le=1.0)
    damage_roi_max_side: int = Field(default=256, ge=32, le=1024)

    enable_egg_roi_inference: bool = Field(default=True)
    roi_padding: float = Field(default=0.12, ge=0.0, le=1.0)
    roi_crack_min_confidence: float = Field(default=0.25, ge=0.0, le=1.0)

    @field_validator("model_path", mode="before")
    @classmethod
    def resolve_model_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path.resolve()

    def cors_origin_list(self) -> list[str]:
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
