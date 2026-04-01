"""Anti-detection and stealth measures for browser automation."""

import random

from playwright.async_api import Page

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) "
    "Gecko/20100101 Firefox/133.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]

# JavaScript to inject for stealth mode
STEALTH_SCRIPT = """
() => {
    // Override navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });

    // Override navigator.plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });

    // Override navigator.languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });

    // Override chrome runtime
    window.chrome = { runtime: {} };

    // Override permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);
}
"""


class AntiDetection:
    """Stealth measures to avoid bot detection."""

    def __init__(self, user_agent: str | None = None) -> None:
        self._user_agent = user_agent or random.choice(USER_AGENTS)
        self._viewport = random.choice(VIEWPORTS)

    def get_user_agent(self) -> str:
        """Get a randomized user agent string."""
        return self._user_agent

    def get_viewport(self) -> dict:
        """Get a randomized viewport size."""
        return self._viewport.copy()

    def get_launch_args(self) -> list[str]:
        """Get browser launch arguments for stealth."""
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--window-size=" f"{self._viewport['width']},{self._viewport['height']}",
        ]

    async def apply_stealth(self, page: Page) -> None:
        """Apply stealth JavaScript to a page."""
        await page.evaluate(STEALTH_SCRIPT)

    def rotate_user_agent(self) -> str:
        """Get a new random user agent."""
        self._user_agent = random.choice(USER_AGENTS)
        return self._user_agent
