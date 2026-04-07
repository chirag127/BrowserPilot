"""Browser action execution with retry and verification."""

import asyncio
import random

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from browser_pilot.logging import get_logger
from browser_pilot.models.action import Action, ActionType
from browser_pilot.models.dom import DOMElement

logger = get_logger(__name__)


class ActionResult:
    """Result of a browser action execution."""

    def __init__(
        self,
        success: bool,
        action_type: str,
        error: str | None = None,
        extracted_text: str = "",
    ) -> None:
        self.success = success
        self.action_type = action_type
        self.error = error
        self.extracted_text = extracted_text


class BrowserActions:
    """Execute browser actions with human-like behavior and retry logic."""

    def __init__(self, page: Page) -> None:
        self._page = page

    async def execute(self, action: Action, elements: list[DOMElement]) -> ActionResult:
        """Execute an action based on its type.

        Args:
            action: The action to execute.
            elements: Current DOM elements for element lookup.

        Returns:
            ActionResult with success/failure info.
        """
        try:
            match action.action_type:
                case ActionType.CLICK:
                    return await self._click(action, elements)
                case ActionType.TYPE:
                    return await self._type_text(action, elements)
                case ActionType.SCROLL:
                    return await self._scroll(action)
                case ActionType.NAVIGATE:
                    return await self._navigate(action)
                case ActionType.SELECT:
                    return await self._select(action, elements)
                case ActionType.HOVER:
                    return await self._hover(action, elements)
                case ActionType.WAIT:
                    return await self._wait(action)
                case ActionType.GO_BACK:
                    return await self._go_back()
                case ActionType.PRESS_KEY:
                    return await self._press_key(action)
                case ActionType.EXTRACT:
                    return await self._extract(action, elements)
                case _:
                    return ActionResult(
                        success=False,
                        action_type=action.action_type.value,
                        error=f"Unsupported action: {action.action_type}",
                    )
        except PlaywrightTimeout as e:
            return ActionResult(
                success=False,
                action_type=action.action_type.value,
                error=f"Timeout: {e}",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=action.action_type.value,
                error=str(e),
            )

    def _find_element(
        self, elements: list[DOMElement], index: int
    ) -> DOMElement | None:
        """Find element by index."""
        for el in elements:
            if el.index == index:
                return el
        return None

    async def _click(self, action: Action, elements: list[DOMElement]) -> ActionResult:
        """Click on an element with human-like behavior."""
        element = self._find_element(elements, action.target_element_index or 0)
        if not element or not element.selector:
            return ActionResult(
                success=False,
                action_type="click",
                error="Element not found or has no selector",
            )

        await self._human_delay(0.1, 0.3)
        await self._page.click(
            element.selector,
            timeout=10000,
        )
        await self._page.wait_for_load_state("domcontentloaded", timeout=5000)

        logger.info("clicked", element=element.selector, text=element.text[:50])
        return ActionResult(success=True, action_type="click")

    async def _type_text(
        self, action: Action, elements: list[DOMElement]
    ) -> ActionResult:
        """Type text into an input field."""
        element = self._find_element(elements, action.target_element_index or 0)
        text = action.params.get("text", "")
        if not element or not element.selector:
            return ActionResult(
                success=False,
                action_type="type",
                error="Element not found",
            )

        await self._page.click(element.selector, timeout=10000)
        await self._page.keyboard.press("Control+a")
        await self._human_delay(0.05, 0.15)
        await self._page.type(element.selector, text, delay=50)

        logger.info("typed", element=element.selector, text=text[:50])
        return ActionResult(success=True, action_type="type")

    async def _scroll(self, action: Action) -> ActionResult:
        """Scroll the page."""
        direction = action.params.get("direction", "down")
        amount = action.params.get("amount", 500)

        if direction == "down":
            await self._page.mouse.wheel(0, amount)
        elif direction == "up":
            await self._page.mouse.wheel(0, -amount)
        elif direction == "left":
            await self._page.mouse.wheel(-amount, 0)
        elif direction == "right":
            await self._page.mouse.wheel(amount, 0)

        await self._human_delay(0.3, 0.7)
        logger.info("scrolled", direction=direction, amount=amount)
        return ActionResult(success=True, action_type="scroll")

    async def _navigate(self, action: Action) -> ActionResult:
        """Navigate to a URL."""
        url = action.params.get("url", "")
        if not url:
            return ActionResult(
                success=False,
                action_type="navigate",
                error="No URL provided",
            )
        await self._page.goto(url, wait_until="domcontentloaded")
        await self._page.wait_for_load_state("networkidle", timeout=10000)
        logger.info("navigated", url=url)
        return ActionResult(success=True, action_type="navigate")

    async def _select(self, action: Action, elements: list[DOMElement]) -> ActionResult:
        """Select a dropdown option."""
        element = self._find_element(elements, action.target_element_index or 0)
        value = action.params.get("value", "")
        if not element or not element.selector:
            return ActionResult(
                success=False,
                action_type="select",
                error="Element not found",
            )
        await self._page.select_option(element.selector, value)
        logger.info("selected", element=element.selector, value=value)
        return ActionResult(success=True, action_type="select")

    async def _hover(self, action: Action, elements: list[DOMElement]) -> ActionResult:
        """Hover over an element."""
        element = self._find_element(elements, action.target_element_index or 0)
        if not element or not element.selector:
            return ActionResult(
                success=False,
                action_type="hover",
                error="Element not found",
            )
        await self._page.hover(element.selector, timeout=10000)
        await self._human_delay(0.2, 0.5)
        logger.info("hovered", element=element.selector)
        return ActionResult(success=True, action_type="hover")

    async def _wait(self, action: Action) -> ActionResult:
        """Wait for a duration or element."""
        seconds = action.params.get("seconds", 1.0)
        selector = action.params.get("selector", "")

        if selector:
            await self._page.wait_for_selector(selector, timeout=int(seconds * 1000))
        else:
            await asyncio.sleep(seconds)

        logger.info("waited", seconds=seconds)
        return ActionResult(success=True, action_type="wait")

    async def _go_back(self) -> ActionResult:
        """Navigate back."""
        await self._page.go_back(wait_until="domcontentloaded")
        logger.info("went_back")
        return ActionResult(success=True, action_type="go_back")

    async def _press_key(self, action: Action) -> ActionResult:
        """Press a keyboard key."""
        key = action.params.get("key", "Enter")
        await self._page.keyboard.press(key)
        await self._human_delay(0.1, 0.3)
        logger.info("pressed_key", key=key)
        return ActionResult(success=True, action_type="press_key")

    async def _extract(
        self, action: Action, elements: list[DOMElement]
    ) -> ActionResult:
        """Extract text from an element or page metadata."""
        # If no specific element is targeted, extract page metadata
        if not action.target_element_index or action.target_element_index == 0:
            # Try to extract page title and metadata
            page_title = await self._page.title()
            page_url = self._page.url
            text = f"Title: {page_title}\nURL: {page_url}"
            logger.info(
                "extracted_page_metadata",
                title=page_title,
                url=page_url,
            )
            return ActionResult(
                success=True,
                action_type="extract",
                extracted_text=text,
            )

        # Otherwise extract text from a specific element
        element = self._find_element(elements, action.target_element_index)
        if not element or not element.selector:
            return ActionResult(
                success=False,
                action_type="extract",
                error="Element not found",
            )
        text = await self._page.text_content(element.selector)
        logger.info("extracted", element=element.selector, text=(text or "")[:100])
        return ActionResult(
            success=True,
            action_type="extract",
            extracted_text=text or "",
        )

    @staticmethod
    async def _human_delay(min_s: float = 0.1, max_s: float = 0.5) -> None:
        """Sleep for a random human-like duration."""
        await asyncio.sleep(random.uniform(min_s, max_s))
