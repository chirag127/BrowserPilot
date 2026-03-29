"""Form interaction tools for LangChain integration."""

from langchain_core.tools import tool
from playwright.async_api import Page


def create_form_tools(page: Page) -> list:
    """Create form interaction tools bound to a specific page.

    Args:
        page: Playwright page instance.

    Returns:
        List of LangChain tools.
    """

    @tool
    async def fill_input(selector: str, value: str) -> str:
        """Fill a form input field with a value.

        Args:
            selector: CSS selector for the input.
            value: Value to fill in.
        """
        try:
            await page.fill(selector, value)
            return f"Filled {selector} with '{value[:50]}'"
        except Exception as e:
            return f"Fill failed: {e}"

    @tool
    async def select_dropdown(selector: str, value: str) -> str:
        """Select an option from a dropdown.

        Args:
            selector: CSS selector for the <select> element.
            value: Option value to select.
        """
        try:
            await page.select_option(selector, value)
            return f"Selected '{value}' in {selector}"
        except Exception as e:
            return f"Select failed: {e}"

    @tool
    async def check_checkbox(selector: str) -> str:
        """Check a checkbox element.

        Args:
            selector: CSS selector for the checkbox.
        """
        try:
            await page.check(selector)
            return f"Checked {selector}"
        except Exception as e:
            return f"Check failed: {e}"

    @tool
    async def submit_form(selector: str = "form") -> str:
        """Submit a form by pressing Enter or clicking submit.

        Args:
            selector: CSS selector for the form or submit button.
        """
        try:
            submit_btn = await page.query_selector(
                f"{selector} [type='submit'], {selector} button"
            )
            if submit_btn:
                await submit_btn.click()
            else:
                await page.keyboard.press("Enter")
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            return f"Form submitted. URL: {page.url}"
        except Exception as e:
            return f"Submit failed: {e}"

    return [
        fill_input,
        select_dropdown,
        check_checkbox,
        submit_form,
    ]
