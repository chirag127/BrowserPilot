"""Health check route."""

from fastapi import APIRouter

from browser_pilot.config import get_settings
from browser_pilot.server.schemas import HealthResponse

health_router = APIRouter()


@health_router.get("/health")
async def health_check() -> HealthResponse:
    """Check server health and provider availability."""
    settings = get_settings()

    # Check Ollama availability
    ollama_ok = False
    try:
        import aiohttp

        async with (
            aiohttp.ClientSession() as session,
            session.get(
                f"{settings.ollama_base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp,
        ):
            ollama_ok = resp.status == 200
    except Exception:
        pass

    # Check OpenRouter availability
    openrouter_ok = bool(settings.openrouter_api_key)

    return HealthResponse(
        status="ok",
        ollama_available=ollama_ok,
        openrouter_available=openrouter_ok,
    )
