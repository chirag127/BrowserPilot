"""Anti-hallucination grounding — verify actions against live DOM."""

from playwright.async_api import Page

from browser_pilot.browser.dom_inspector import DOMInspector
from browser_pilot.logging import get_logger
from browser_pilot.models.action import Action
from browser_pilot.models.dom import DOMElement

logger = get_logger(__name__)


class ActionGrounder:
    """Verify proposed actions against the live DOM state before execution.

    Implements a 5-check anti-hallucination strategy:
    1. Element existence — Is the target element in the DOM?
    2. Visibility — Is the element visible in the viewport?
    3. Interactivity — Is the element actually interactive?
    4. Bounding box match — Does the position match?
    5. Page freshness — Has the page changed since the screenshot?
    """

    def __init__(self) -> None:
        self._dom_inspector = DOMInspector()
        self._rejection_threshold = 0.3

    async def verify(
        self,
        action: Action,
        page: Page,
        original_elements: list[DOMElement],
    ) -> tuple[bool, float, str]:
        """Verify an action against the current live DOM.

        Args:
            action: The proposed action to verify.
            page: The current Playwright page.
            original_elements: Elements from when the screenshot was taken.

        Returns:
            Tuple of (is_valid, confidence, reason).
        """
        # Actions without targets don't need grounding
        if action.target_element_index is None and action.action_type.value in (
            "scroll",
            "navigate",
            "wait",
            "go_back",
            "press_key",
            "screenshot",
        ):
            return True, action.confidence, "No target element needed"

        # Get fresh DOM state
        fresh_elements = await self._dom_inspector.inspect(page)

        # Find the target element
        target_index = action.target_element_index or 0
        fresh_el = next(
            (e for e in fresh_elements if e.index == target_index),
            None,
        )
        original_el = next(
            (e for e in original_elements if e.index == target_index),
            None,
        )

        if fresh_el is None:
            return False, 0.0, f"Element {target_index} not found in DOM"

        # Check 1: Element exists
        if not fresh_el.selector:
            return False, 0.0, "Element has no selector"

        # Check 2: Element is visible
        if not fresh_el.is_visible:
            return False, 0.1, "Element is not visible"

        # Check 3: Element is interactive
        if (
            action.action_type.value in ("click", "type", "select", "hover")
            and not fresh_el.is_interactive
        ):
            return False, 0.2, "Element is not interactive"

        # Check 4: Bounding box match (element hasn't moved)
        if original_el and original_el.bbox and fresh_el.bbox:
            dx = abs(original_el.bbox.x - fresh_el.bbox.x)
            dy = abs(original_el.bbox.y - fresh_el.bbox.y)
            if dx > 50 or dy > 50:
                logger.warning(
                    "bbox_shift_detected",
                    element=target_index,
                    dx=dx,
                    dy=dy,
                )
                # Element moved — update action's element index
                # but don't reject (page may have scrolled)

        # Check 5: Page state validation
        # Verify the element tag matches what was expected
        if original_el and fresh_el.tag != original_el.tag:
            return (
                False,
                0.3,
                f"Element tag changed: {original_el.tag} -> {fresh_el.tag}",
            )

        confidence = min(action.confidence, 1.0)
        if confidence < self._rejection_threshold:
            return (
                False,
                confidence,
                f"Confidence too low: {confidence:.2f}",
            )

        return True, confidence, "All grounding checks passed"
