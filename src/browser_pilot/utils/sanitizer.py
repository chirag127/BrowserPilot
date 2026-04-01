"""Input sanitization utilities."""

import re
from urllib.parse import urlparse


def sanitize_url(url: str) -> str:
    """Validate and sanitize a URL.

    Args:
        url: Raw URL string.

    Returns:
        Sanitized URL string.

    Raises:
        ValueError: If URL is invalid or uses disallowed scheme.
    """
    url = url.strip()

    if not url:
        raise ValueError("Empty URL")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Invalid URL scheme: {parsed.scheme}. " "Only http and https are allowed."
        )

    if not parsed.netloc:
        raise ValueError("URL missing hostname")

    return url


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Sanitize user text input.

    Args:
        text: Raw text input.
        max_length: Maximum allowed length.

    Returns:
        Sanitized text.
    """
    # Remove control characters except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def sanitize_selector(selector: str) -> str:
    """Validate a CSS selector for safety.

    Args:
        selector: CSS selector string.

    Returns:
        Validated selector.

    Raises:
        ValueError: If selector contains dangerous patterns.
    """
    dangerous = ["javascript:", "data:", "vbscript:", "<script"]
    lower = selector.lower()
    for pattern in dangerous:
        if pattern in lower:
            raise ValueError(f"Dangerous pattern in selector: {pattern}")

    return selector.strip()
