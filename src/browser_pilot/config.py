"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- LLM: Ollama (primary, local, free) ---
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL",
    )
    ollama_model: str = Field(
        default="gemma3:4b",
        description="Ollama vision model name",
    )

    # --- LLM: OpenRouter (fallback, free tier) ---
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key (free, no credit card)",
    )
    openrouter_model: str = Field(
        default="google/gemma-3-27b-it:free",
        description="OpenRouter free vision model",
    )

    # --- Browser ---
    browser_headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    browser_type: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser engine to use",
    )

    # --- Agent ---
    max_steps: int = Field(
        default=50,
        description="Maximum steps per sub-task",
    )
    step_timeout: int = Field(
        default=120,
        description="Timeout per step in seconds",
    )
    max_failures: int = Field(
        default=5,
        description="Max consecutive failures before abort",
    )

    # --- Server ---
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        default=8000,
        description="API server port",
    )
    api_key: str = Field(
        default="your-api-key-here",
        description="API authentication key",
    )

    # --- Logging ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # --- Storage ---
    screenshot_dir: Path = Field(
        default=Path("./screenshots"),
        description="Screenshot storage directory",
    )
    recording_dir: Path = Field(
        default=Path("./recordings"),
        description="Browser recording directory",
    )

    def get_llm_base_url(self, provider: str = "ollama") -> str:
        """Get the base URL for the specified LLM provider."""
        if provider == "ollama":
            return f"{self.ollama_base_url}/v1"
        elif provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        msg = f"Unknown provider: {provider}"
        raise ValueError(msg)

    def get_llm_api_key(self, provider: str = "ollama") -> str:
        """Get the API key for the specified LLM provider."""
        if provider == "ollama":
            return "ollama"  # Ollama doesn't need a real key
        elif provider == "openrouter":
            if not self.openrouter_api_key:
                msg = (
                    "OpenRouter API key not set. "
                    "Get a free key at https://openrouter.ai"
                )
                raise ValueError(msg)
            return self.openrouter_api_key
        msg = f"Unknown provider: {provider}"
        raise ValueError(msg)

    def get_llm_model(self, provider: str = "ollama") -> str:
        """Get the model name for the specified LLM provider."""
        if provider == "ollama":
            return self.ollama_model
        elif provider == "openrouter":
            return self.openrouter_model
        msg = f"Unknown provider: {provider}"
        raise ValueError(msg)

    def ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.recording_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings."""
    settings = Settings()
    settings.ensure_directories()
    return settings
