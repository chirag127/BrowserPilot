"""Vision pipeline — screenshots, annotation, interpretation."""

from browser_pilot.vision.annotator import DOMAnnotator
from browser_pilot.vision.grounding import ActionGrounder
from browser_pilot.vision.interpreter import VisionInterpreter
from browser_pilot.vision.screenshot import ScreenshotCapture

__all__ = [
    "ActionGrounder",
    "DOMAnnotator",
    "ScreenshotCapture",
    "VisionInterpreter",
]
