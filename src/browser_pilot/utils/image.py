"""Image processing utilities."""

import base64
from io import BytesIO

from PIL import Image


def optimize_screenshot(
    image_bytes: bytes,
    max_width: int = 1280,
    quality: int = 85,
) -> bytes:
    """Resize and compress screenshot for API token efficiency.

    Args:
        image_bytes: Raw PNG/JPEG image bytes.
        max_width: Maximum width in pixels.
        quality: JPEG quality (1-100).

    Returns:
        Optimized image bytes.
    """
    img = Image.open(BytesIO(image_bytes))

    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def from_base64(b64_string: str) -> bytes:
    """Convert base64 string to image bytes."""
    return base64.b64decode(b64_string)


def estimate_tokens(image_bytes: bytes) -> int:
    """Estimate token count for an image (rough approximation).

    OpenAI/Gemini charge ~85 tokens per 512x512 tile.
    """
    img = Image.open(BytesIO(image_bytes))
    tiles_x = (img.width + 511) // 512
    tiles_y = (img.height + 511) // 512
    return tiles_x * tiles_y * 85
