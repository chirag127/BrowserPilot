"""Health check route."""

from fastapi import APIRouter

from browser_pilot.config import get_settings
from browser_pilot.server.schemas import HealthResponse

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> HealthResponse:
    """Check server health and provider availability."""
    settings = get_settings()

    # Check Gemini availability
    gemini_available = bool(settings.google_api_key)

    # Check OpenRouter availability
    openrouter_ok = bool(settings.openrouter_api_key)

    return HealthResponse(
        status="ok",
        gemini_available=gemini_available,
        openrouter_available=openrouter_ok,
    )
