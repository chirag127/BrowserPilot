"""Vision pipeline — screenshots, annotation, interpretation."""

from browser_pilot.vision.screenshot import ScreenshotCapture
from browser_pilot.vision.annotator import DOMAnnotator
from browser_pilot.vision.interpreter import VisionInterpreter
from browser_pilot.vision.grounding import ActionGrounder

__all__ = [
    "ScreenshotCapture",
    "DOMAnnotator",
    "VisionInterpreter",
    "ActionGrounder",
]
