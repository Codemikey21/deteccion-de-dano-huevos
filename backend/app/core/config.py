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
