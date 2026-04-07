"""Tests for input sanitization."""

import pytest

from browser_pilot.utils.sanitizer import (
    sanitize_selector,
    sanitize_text,
    sanitize_url,
)


class TestSanitizeUrl:
    """Test URL sanitization."""

    def test_valid_url(self) -> None:
        assert sanitize_url("https://example.com") == "https://example.com"

    def test_valid_http(self) -> None:
        assert sanitize_url("http://example.com/path") == ("http://example.com/path")

    def test_empty_url(self) -> None:
        with pytest.raises(ValueError, match="Empty URL"):
            sanitize_url("")

    def test_invalid_scheme(self) -> None:
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            sanitize_url("javascript:alert(1)")

    def test_no_hostname(self) -> None:
        with pytest.raises(ValueError, match="missing hostname"):
            sanitize_url("https://")

    def test_strips_whitespace(self) -> None:
        assert sanitize_url("  https://example.com  ") == ("https://example.com")


class TestSanitizeText:
    """Test text sanitization."""

    def test_normal_text(self) -> None:
        assert sanitize_text("Hello world") == "Hello world"

    def test_strips_control_chars(self) -> None:
        assert sanitize_text("Hello\x00world") == "Helloworld"

    def test_truncates_long_text(self) -> None:
        long = "a" * 6000
        result = sanitize_text(long, max_length=100)
        assert len(result) == 100

    def test_strips_whitespace(self) -> None:
        assert sanitize_text("  hello  ") == "hello"


class TestSanitizeSelector:
    """Test selector sanitization."""

    def test_valid_selector(self) -> None:
        assert sanitize_selector("div.class") == "div.class"

    def test_dangerous_javascript(self) -> None:
        with pytest.raises(ValueError, match="Dangerous"):
            sanitize_selector("javascript:alert(1)")

    def test_dangerous_script(self) -> None:
        with pytest.raises(ValueError, match="Dangerous"):
            sanitize_selector("<script>alert(1)</script>")
