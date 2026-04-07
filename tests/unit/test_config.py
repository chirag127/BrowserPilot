"""Tests for configuration module."""

from browser_pilot.config import Settings


class TestSettings:
    """Test Settings class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        settings = Settings(
            google_api_key="",
            gemini_model="gemini-2.0-flash",
            openrouter_api_key="",
            openrouter_model="google/gemma-3-27b-it:free",
        )
        assert settings.google_api_key == ""
        assert settings.gemini_model == "gemini-2.0-flash"
        assert settings.openrouter_api_key == ""
        assert settings.openrouter_model == "google/gemma-3-27b-it:free"

    def test_get_llm_base_url_gemini(self) -> None:
        """Test Gemini base URL (empty string)."""
        settings = Settings()
        url = settings.get_llm_base_url("gemini")
        assert url == ""

    def test_get_llm_base_url_openrouter(self) -> None:
        """Test OpenRouter base URL."""
        settings = Settings()
        url = settings.get_llm_base_url("openrouter")
        assert url == "https://openrouter.ai/api/v1"

    def test_get_llm_api_key_gemini(self) -> None:
        """Test Gemini API key retrieval."""
        settings = Settings(google_api_key="test-gemini-key")
        key = settings.get_llm_api_key("gemini")
        assert key == "test-gemini-key"

    def test_get_llm_api_key_gemini_missing(self) -> None:
        """Test Gemini API key raises when not set."""
        settings = Settings(google_api_key="")
        try:
            settings.get_llm_api_key("gemini")
            raise AssertionError("Should raise ValueError")
        except ValueError as e:
            assert "GOOGLE_API_KEY not set" in str(e)

    def test_get_llm_api_key_openrouter(self) -> None:
        """Test OpenRouter API key retrieval."""
        settings = Settings(openrouter_api_key="test-or-key")
        key = settings.get_llm_api_key("openrouter")
        assert key == "test-or-key"

    def test_get_llm_api_key_openrouter_missing(self) -> None:
        """Test OpenRouter API key raises when not set."""
        settings = Settings(openrouter_api_key="")
        try:
            settings.get_llm_api_key("openrouter")
            raise AssertionError("Should raise ValueError")
        except ValueError as e:
            assert "OpenRouter API key not set" in str(e)

    def test_get_llm_model_gemini(self) -> None:
        """Test Gemini model retrieval."""
        settings = Settings()
        assert settings.get_llm_model("gemini") == "gemini-2.0-flash"

    def test_get_llm_model_gemini_custom(self) -> None:
        """Test custom Gemini model."""
        settings = Settings(gemini_model="gemini-2.0-pro")
        assert settings.get_llm_model("gemini") == "gemini-2.0-pro"

    def test_get_llm_model_openrouter(self) -> None:
        """Test OpenRouter model retrieval."""
        settings = Settings()
        assert settings.get_llm_model("openrouter") == "google/gemma-3-27b-it:free"

    def test_get_llm_model_openrouter_custom(self) -> None:
        """Test custom OpenRouter model."""
        settings = Settings(openrouter_model="meta-llama/llama-3-70b-instruct")
        assert settings.get_llm_model("openrouter") == "meta-llama/llama-3-70b-instruct"

    def test_invalid_provider(self) -> None:
        """Test invalid provider raises error."""
        settings = Settings()
        try:
            settings.get_llm_base_url("invalid")
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass
