"""Navigation tools for LangChain integration."""

from typing import Optional

from langchain_core.tools import tool
from playwright.async_api import Page


def create_navigation_tools(page: Page) -> list:
    """Create navigation tools bound to a specific page.

    Args:
        page: Playwright page instance.

    Returns:
        List of LangChain tools.
    """

    @tool
    async def navigate_to_url(url: str) -> str:
        """Navigate the browser to a specific URL.

        Args:
            url: The URL to navigate to.
        """
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            title = await page.title()
            return f"Navigated to {url}. Page title: {title}"
        except Exception as e:
            return f"Navigation failed: {e}"

    @tool
    async def go_back() -> str:
        """Go back to the previous page in browser history."""
        try:
            await page.go_back(wait_until="domcontentloaded")
            return f"Navigated back to {page.url}"
        except Exception as e:
            return f"Go back failed: {e}"

    @tool
    async def go_forward() -> str:
        """Go forward to the next page in browser history."""
        try:
            await page.go_forward(wait_until="domcontentloaded")
            return f"Navigated forward to {page.url}"
        except Exception as e:
            return f"Go forward failed: {e}"

    @tool
    async def refresh_page() -> str:
        """Refresh the current page."""
        try:
            await page.reload(wait_until="domcontentloaded")
            return f"Page refreshed. URL: {page.url}"
        except Exception as e:
            return f"Refresh failed: {e}"

    return [
        navigate_to_url,
        go_back,
        go_forward,
        refresh_page,
    ]
