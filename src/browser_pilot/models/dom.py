"""DOM element models."""

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates of an element."""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


class DOMElement(BaseModel):
    """Represents a DOM element extracted from the page."""

    index: int = 0
    tag: str = ""
    text: str = ""
    attributes: dict = Field(default_factory=dict)
    bbox: BoundingBox | None = None
    is_interactive: bool = False
    is_visible: bool = True
    selector: str = ""
    aria_label: str = ""
    placeholder: str = ""
    role: str = ""
