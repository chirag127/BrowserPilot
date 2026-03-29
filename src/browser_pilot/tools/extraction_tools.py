"""Data extraction tools for LangChain integration."""

from langchain_core.tools import tool
from playwright.async_api import Page


def create_extraction_tools(page: Page) -> list:
    """Create data extraction tools bound to a specific page.

    Args:
        page: Playwright page instance.

    Returns:
        List of LangChain tools.
    """

    @tool
    async def extract_text(selector: str) -> str:
        """Extract text content from elements matching a selector.

        Args:
            selector: CSS selector for elements to extract text from.
        """
        try:
            elements = await page.query_selector_all(selector)
            texts = []
            for el in elements:
                text = await el.text_content()
                if text and text.strip():
                    texts.append(text.strip())
            return "\n".join(texts) if texts else "No text found"
        except Exception as e:
            return f"Extract failed: {e}"

    @tool
    async def extract_table(selector: str = "table") -> str:
        """Extract table data as structured text.

        Args:
            selector: CSS selector for the table element.
        """
        try:
            table = await page.query_selector(selector)
            if not table:
                return "No table found"

            rows = await table.query_selector_all("tr")
            result = []
            for row in rows:
                cells = await row.query_selector_all("th, td")
                row_data = []
                for cell in cells:
                    text = await cell.text_content()
                    row_data.append((text or "").strip())
                if row_data:
                    result.append(" | ".join(row_data))

            return "\n".join(result) if result else "Empty table"
        except Exception as e:
            return f"Table extract failed: {e}"

    @tool
    async def extract_links() -> str:
        """Extract all links from the current page."""
        try:
            links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({
                        text: a.innerText.trim().substring(0, 100),
                        href: a.href
                    }))
                    .filter(l => l.text)
                    .slice(0, 50)
            }""")
            result = []
            for link in links:
                result.append(f"- {link['text']}: {link['href']}")
            return "\n".join(result) if result else "No links found"
        except Exception as e:
            return f"Links extract failed: {e}"

    @tool
    async def get_page_title() -> str:
        """Get the title of the current page."""
        try:
            return await page.title()
        except Exception as e:
            return f"Title fetch failed: {e}"

    return [
        extract_text,
        extract_table,
        extract_links,
        get_page_title,
    ]
