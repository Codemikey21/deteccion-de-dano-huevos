"""Punto de entrada FastAPI — Egg Detection API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import health, predict
from backend.app.core.config import get_settings
from backend.app.core.constants import API_TITLE, API_VERSION
from backend.app.schemas.prediction import RootResponse
from backend.app.services.inference import get_inference_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    inference = get_inference_service()
    loaded = inference.load(settings.model_path)
    if loaded:
        print(f"Modelo cargado: {settings.model_path}")
    else:
        print(f"ADVERTENCIA — modelo no cargado: {inference.load_error}")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(predict.router)

    @app.get("/", response_model=RootResponse)
    def root() -> RootResponse:
        return RootResponse(name=API_TITLE, version=API_VERSION, docs="/docs")

    return app


app = create_app()
