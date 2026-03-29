"""FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from browser_pilot.config import get_settings
from browser_pilot.logging import configure_logging, get_logger
from browser_pilot.server.routes.health import health_router
from browser_pilot.server.routes.tasks import tasks_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info(
        "server_starting",
        host=settings.api_host,
        port=settings.api_port,
    )
    yield
    logger.info("server_stopping")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="BrowserPilot",
        description="Autonomous browser agent powered by local AI",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])

    return app
