"""Browser automation layer — Playwright controller."""

from browser_pilot.browser.actions import BrowserActions
from browser_pilot.browser.anti_detection import AntiDetection
from browser_pilot.browser.controller import BrowserController
from browser_pilot.browser.dom_inspector import DOMInspector

__all__ = [
    "AntiDetection",
    "BrowserActions",
    "BrowserController",
    "DOMInspector",
]
