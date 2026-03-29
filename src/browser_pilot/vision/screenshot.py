"""Screenshot capture and processing."""

import time

from PIL import Image
from playwright.async_api import Page

from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger

logger = get_logger(__name__)


class ScreenshotCapture:
    """Capture and process browser screenshots."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._counter = 0

    async def capture(
        self,
        page: Page,
        full_page: bool = False,
        optimize: bool = True,
    ) -> bytes:
        """Take a screenshot of the current page.

        Args:
            page: Playwright page instance.
            full_page: If True, capture entire scrollable page.
            optimize: If True, resize and compress for API efficiency.

        Returns:
            Screenshot as PNG bytes.
        """
        self._counter += 1
        screenshot_bytes = await page.screenshot(
            full_page=full_page,
            type="png",
        )

        if optimize:
            screenshot_bytes = self._optimize(screenshot_bytes)

        # Save to disk
        filename = f"step_{self._counter:04d}_{int(time.time())}.png"
        filepath = self._settings.screenshot_dir / filename
        with open(filepath, "wb") as f:
            f.write(screenshot_bytes)

        logger.info(
            "screenshot_captured",
            path=str(filepath),
            size=len(screenshot_bytes),
            full_page=full_page,
        )

        return screenshot_bytes

    async def capture_element(self, page: Page, selector: str) -> bytes | None:
        """Take a screenshot of a specific element."""
        element = await page.query_selector(selector)
        if not element:
            logger.warning("element_not_found", selector=selector)
            return None

        screenshot_bytes = await element.screenshot(type="png")
        return self._optimize(screenshot_bytes)

    def _optimize(self, image_bytes: bytes, max_width: int = 1280) -> bytes:
        """Resize and compress screenshot for API token efficiency."""
        from io import BytesIO

        img = Image.open(BytesIO(image_bytes))

        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()

    def get_screenshot_paths(self) -> list[str]:
        """Get all saved screenshot paths."""
        return sorted(
            str(p) for p in self._settings.screenshot_dir.glob("step_*.png")
        )

    @staticmethod
    def to_base64(image_bytes: bytes) -> str:
        """Convert image bytes to base64 string."""
        import base64

        return base64.b64encode(image_bytes).decode("utf-8")
