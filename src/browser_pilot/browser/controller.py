"""Playwright browser controller with lifecycle management."""

import asyncio
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from browser_pilot.browser.anti_detection import AntiDetection
from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger, log_timing

logger = get_logger(__name__)


class BrowserController:
    """Manages Playwright browser lifecycle and page navigation."""

    def __init__(self) -> None:
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._settings = get_settings()
        self._anti_detection = AntiDetection()
        self._lock = asyncio.Lock()

    @property
    def page(self) -> Page:
        """Get the current page, raising if not initialized."""
        if self._page is None:
            msg = "Browser not started. Call start() first."
            raise RuntimeError(msg)
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Get the current browser context."""
        if self._context is None:
            msg = "Browser not started. Call start() first."
            raise RuntimeError(msg)
        return self._context

    @property
    def is_running(self) -> bool:
        """Check if browser is currently running."""
        return self._browser is not None and self._page is not None

    async def start(self) -> None:
        """Launch browser and create a new context/page."""
        async with self._lock:
            if self.is_running:
                return

            with log_timing(logger, "browser_start"):
                settings = self._settings
                self._playwright = await async_playwright().start()

                browser_type = getattr(self._playwright, settings.browser_type)
                self._browser = await browser_type.launch(
                    headless=settings.browser_headless,
                    args=self._anti_detection.get_launch_args(),
                )

                viewport = self._anti_detection.get_viewport()
                user_agent = self._anti_detection.get_user_agent()

                self._context = await self._browser.new_context(
                    viewport=viewport,
                    user_agent=user_agent,
                    locale="en-US",
                    timezone_id="America/New_York",
                )

                if settings.recording_dir:
                    self._context = await self._browser.new_context(
                        viewport=viewport,
                        user_agent=user_agent,
                        locale="en-US",
                        timezone_id="America/New_York",
                        record_video_dir=str(settings.recording_dir),
                        record_video_size=viewport,
                    )

                self._page = await self._context.new_page()
                await self._anti_detection.apply_stealth(self._page)

            logger.info(
                "browser_started",
                type=settings.browser_type,
                headless=settings.browser_headless,
                viewport=viewport,
            )

    async def stop(self) -> None:
        """Close browser and clean up resources."""
        async with self._lock:
            with log_timing(logger, "browser_stop"):
                if self._page:
                    await self._page.close()
                    self._page = None
                if self._context:
                    await self._context.close()
                    self._context = None
                if self._browser:
                    await self._browser.close()
                    self._browser = None
                if self._playwright:
                    await self._playwright.stop()
                    self._playwright = None

            logger.info("browser_stopped")

    async def restart(self) -> None:
        """Restart the browser (useful after crashes)."""
        await self.stop()
        await self.start()

    async def navigate(self, url: str) -> None:
        """Navigate to a URL and wait for load."""
        with log_timing(logger, "navigate", url=url):
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        logger.info("navigated", url=url, title=await self.page.title())

    async def go_back(self) -> None:
        """Navigate back in history."""
        await self.page.go_back(wait_until="domcontentloaded")
        logger.info("navigated_back")

    async def go_forward(self) -> None:
        """Navigate forward in history."""
        await self.page.go_forward(wait_until="domcontentloaded")
        logger.info("navigated_forward")

    async def refresh(self) -> None:
        """Refresh the current page."""
        await self.page.reload(wait_until="domcontentloaded")
        logger.info("page_refreshed")

    async def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    async def get_title(self) -> str:
        """Get the current page title."""
        return await self.page.title()

    async def __aenter__(self) -> "BrowserController":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
