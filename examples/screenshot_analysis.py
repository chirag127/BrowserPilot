"""Example: Take a screenshot and analyze it."""

import asyncio

from browser_pilot.browser.controller import BrowserController
from browser_pilot.vision.screenshot import ScreenshotCapture


async def main() -> None:
    """Navigate to a page and capture a screenshot."""
    async with BrowserController() as browser:
        await browser.navigate("https://example.com")

        capture = ScreenshotCapture()
        screenshot = await capture.capture(browser.page)

        b64 = capture.to_base64(screenshot)
        print(f"Screenshot captured: {len(screenshot)} bytes")
        print(f"Base64 length: {len(b64)} chars")
        print(f"Saved to: {capture.get_screenshot_paths()}")


if __name__ == "__main__":
    asyncio.run(main())
