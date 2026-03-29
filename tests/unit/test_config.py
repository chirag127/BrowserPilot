"""Tests for configuration module."""

from browser_pilot.config import Settings


class TestSettings:
    """Test Settings class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        settings = Settings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "gemma3:4b"
        assert settings.browser_headless is True
        assert settings.browser_type == "chromium"
        assert settings.max_steps == 50
        assert settings.api_port == 8000

    def test_get_llm_base_url_ollama(self) -> None:
        """Test Ollama base URL generation."""
        settings = Settings()
        url = settings.get_llm_base_url("ollama")
        assert url == "http://localhost:11434/v1"

    def test_get_llm_base_url_openrouter(self) -> None:
        """Test OpenRouter base URL."""
        settings = Settings()
        url = settings.get_llm_base_url("openrouter")
        assert url == "https://openrouter.ai/api/v1"

    def test_get_llm_api_key_ollama(self) -> None:
        """Test Ollama API key (should be dummy)."""
        settings = Settings()
        key = settings.get_llm_api_key("ollama")
        assert key == "ollama"

    def test_get_llm_api_key_openrouter_missing(self) -> None:
        """Test OpenRouter API key raises when not set."""
        settings = Settings(openrouter_api_key="")
        try:
            settings.get_llm_api_key("openrouter")
            raise AssertionError("Should raise ValueError")
        except ValueError as e:
            assert "OpenRouter API key not set" in str(e)

    def test_get_llm_model(self) -> None:
        """Test model name retrieval."""
        settings = Settings()
        assert settings.get_llm_model("ollama") == "gemma3:4b"
        assert (
            settings.get_llm_model("openrouter") == "google/gemma-3-27b-it:free"
        )

    def test_invalid_provider(self) -> None:
        """Test invalid provider raises error."""
        settings = Settings()
        try:
            settings.get_llm_base_url("invalid")
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass
