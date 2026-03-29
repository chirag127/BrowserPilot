"""Browser action tools for LangChain integration."""

from typing import Optional

from langchain_core.tools import tool
from playwright.async_api import Page


def create_browser_tools(page: Page) -> list:
    """Create browser action tools bound to a specific page.

    Args:
        page: Playwright page instance.

    Returns:
        List of LangChain tools.
    """

    @tool
    async def click_element(selector: str) -> str:
        """Click on a web element identified by CSS selector.

        Args:
            selector: CSS selector for the element to click.
        """
        try:
            await page.click(selector, timeout=10000)
            return f"Successfully clicked element: {selector}"
        except Exception as e:
            return f"Failed to click {selector}: {e}"

    @tool
    async def type_text(selector: str, text: str) -> str:
        """Type text into an input field.

        Args:
            selector: CSS selector for the input element.
            text: Text to type.
        """
        try:
            await page.click(selector, timeout=5000)
            await page.fill(selector, text)
            return f"Typed '{text[:50]}' into {selector}"
        except Exception as e:
            return f"Failed to type into {selector}: {e}"

    @tool
    async def scroll_page(direction: str = "down", amount: int = 500) -> str:
        """Scroll the page up or down.

        Args:
            direction: Scroll direction ('up', 'down', 'left', 'right').
            amount: Number of pixels to scroll.
        """
        try:
            if direction == "down":
                await page.mouse.wheel(0, amount)
            elif direction == "up":
                await page.mouse.wheel(0, -amount)
            elif direction == "right":
                await page.mouse.wheel(amount, 0)
            elif direction == "left":
                await page.mouse.wheel(-amount, 0)
            return f"Scrolled {direction} by {amount}px"
        except Exception as e:
            return f"Scroll failed: {e}"

    @tool
    async def get_page_text() -> str:
        """Get the visible text content of the current page."""
        try:
            text = await page.evaluate(
                "() => document.body.innerText.substring(0, 3000)"
            )
            return text or "No text content found"
        except Exception as e:
            return f"Failed to get text: {e}"

    @tool
    async def get_current_url() -> str:
        """Get the current page URL."""
        return page.url

    return [
        click_element,
        type_text,
        scroll_page,
        get_page_text,
        get_current_url,
    ]
