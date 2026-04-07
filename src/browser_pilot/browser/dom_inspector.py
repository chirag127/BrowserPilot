"""DOM tree extraction and inspection."""

from playwright.async_api import Page

from browser_pilot.logging import get_logger
from browser_pilot.models.dom import BoundingBox, DOMElement

logger = get_logger(__name__)

# JavaScript to extract interactive DOM elements with bounding boxes
DOM_EXTRACTION_SCRIPT = """
() => {
    const elements = [];
    const interactiveSelectors = [
        'a[href]', 'button', 'input', 'select', 'textarea',
        '[role="button"]', '[role="link"]', '[role="checkbox"]',
        '[role="radio"]', '[role="textbox"]', '[role="combobox"]',
        '[role="menuitem"]', '[role="tab"]', '[onclick]',
        '[contenteditable="true"]', 'details > summary',
        'label[for]', '[tabindex]:not([tabindex="-1"])',
    ];

    const selector = interactiveSelectors.join(', ');
    const nodes = document.querySelectorAll(selector);

    nodes.forEach((node, index) => {
        const rect = node.getBoundingClientRect();
        const style = window.getComputedStyle(node);

        if (
            rect.width === 0 || rect.height === 0 ||
            style.display === 'none' ||
            style.visibility === 'hidden' ||
            style.opacity === '0'
        ) {
            return;
        }

        const text = (node.innerText || node.value || node.placeholder || '')
            .trim().substring(0, 200);

        const attrs = {};
        for (const attr of node.attributes) {
            if (['id', 'name', 'type', 'href', 'aria-label',
                 'placeholder', 'value', 'role', 'data-testid'].includes(attr.name)) {
                attrs[attr.name] = attr.value.substring(0, 200);
            }
        }

        elements.push({
            index: elements.length,
            tag: node.tagName.toLowerCase(),
            text: text,
            attributes: attrs,
            bbox: {
                x: rect.x,
                y: rect.y + window.scrollY,
                width: rect.width,
                height: rect.height,
            },
            is_interactive: true,
            is_visible: true,
            selector: _buildSelector(node),
            aria_label: node.getAttribute('aria-label') || '',
            placeholder: node.getAttribute('placeholder') || '',
            role: node.getAttribute('role') || '',
        });
    });

    function _buildSelector(el) {
        if (el.id) return '#' + CSS.escape(el.id);
        if (el.getAttribute('data-testid'))
            return `[data-testid="${el.getAttribute('data-testid')}"]`;

        let path = [];
        while (el && el.nodeType === 1) {
            let seg = el.tagName.toLowerCase();
            if (el.id) {
                path.unshift('#' + CSS.escape(el.id));
                break;
            }
            const parent = el.parentNode;
            if (parent) {
                const siblings = Array.from(parent.children)
                    .filter(c => c.tagName === el.tagName);
                if (siblings.length > 1) {
                    seg += ':nth-of-type(' +
                        (siblings.indexOf(el) + 1) + ')';
                }
            }
            path.unshift(seg);
            el = el.parentNode;
        }
        return path.join(' > ');
    }

    return elements;
}
"""


class DOMInspector:
    """Extract and analyze DOM structure from a Playwright page."""

    async def inspect(
        self,
        page: Page,
        interactive_only: bool = True,
    ) -> list[DOMElement]:
        """Extract DOM elements from the current page.

        Args:
            page: Playwright page instance.
            interactive_only: If True, only return interactive elements.

        Returns:
            List of DOMElement instances.
        """
        raw_elements = await page.evaluate(DOM_EXTRACTION_SCRIPT)

        elements = []
        for raw in raw_elements:
            try:
                bbox = None
                if raw.get("bbox"):
                    bbox = BoundingBox(**raw["bbox"])

                element = DOMElement(
                    index=raw.get("index", len(elements)),
                    tag=raw.get("tag", ""),
                    text=raw.get("text", ""),
                    attributes=raw.get("attributes", {}),
                    bbox=bbox,
                    is_interactive=raw.get("is_interactive", True),
                    is_visible=raw.get("is_visible", True),
                    selector=raw.get("selector", ""),
                    aria_label=raw.get("aria_label", ""),
                    placeholder=raw.get("placeholder", ""),
                    role=raw.get("role", ""),
                )
                elements.append(element)
            except Exception as e:
                logger.warning(
                    "dom_parse_error",
                    error=str(e),
                    raw=raw,
                )

        logger.info(
            "dom_inspected",
            total=len(elements),
            interactive=sum(1 for e in elements if e.is_interactive),
        )
        return elements

    async def get_page_text(self, page: Page) -> str:
        """Extract visible text content from the page."""
        text = await page.evaluate("() => document.body.innerText.substring(0, 5000)")
        return text or ""

    async def get_page_metadata(self, page: Page) -> dict:
        """Extract page metadata (title, URL, description)."""
        return await page.evaluate("""() => ({
            title: document.title,
            url: window.location.href,
            description: document.querySelector('meta[name="description"]')
                ?.content || '',
            h1: document.querySelector('h1')?.innerText || '',
        })""")
