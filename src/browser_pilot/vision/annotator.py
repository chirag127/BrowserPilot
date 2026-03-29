"""DOM element annotation with Set-of-Marks overlay."""

from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from browser_pilot.models.dom import DOMElement

# Color palette for element types (BGR for consistency)
ELEMENT_COLORS = {
    "a": (66, 133, 244),  # Blue — links
    "button": (234, 67, 53),  # Red — buttons
    "input": (52, 168, 83),  # Green — inputs
    "select": (251, 188, 4),  # Yellow — dropdowns
    "textarea": (171, 71, 188),  # Purple — textareas
    "default": (128, 128, 128),  # Gray — other
}


class DOMAnnotator:
    """Overlay numbered bounding boxes on screenshots for vision grounding.

    Uses the Set-of-Marks (SoM) technique to label interactive elements
    with numbered indices that the vision model can reference.
    """

    def annotate(
        self,
        screenshot_bytes: bytes,
        elements: list[DOMElement],
        label_size: int = 18,
        padding: int = 4,
    ) -> bytes:
        """Draw numbered bounding boxes on a screenshot.

        Args:
            screenshot_bytes: Raw PNG screenshot.
            elements: DOM elements with bounding boxes.
            label_size: Font size for element labels.
            padding: Padding around labels.

        Returns:
            Annotated screenshot as PNG bytes.
        """
        img = Image.open(BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", label_size)
        except OSError:
            font = ImageFont.load_default()

        for element in elements:
            if not element.bbox or not element.is_visible:
                continue

            bbox = element.bbox
            color = ELEMENT_COLORS.get(element.tag, ELEMENT_COLORS["default"])

            # Draw bounding box
            draw.rectangle(
                [
                    (bbox.x, bbox.y),
                    (bbox.x + bbox.width, bbox.y + bbox.height),
                ],
                outline=color,
                width=2,
            )

            # Draw label background
            label = str(element.index)
            bbox_text = draw.textbbox((0, 0), label, font=font)
            label_w = bbox_text[2] - bbox_text[0] + padding * 2
            label_h = bbox_text[3] - bbox_text[1] + padding * 2

            label_x = bbox.x
            label_y = max(0, bbox.y - label_h)

            draw.rectangle(
                [
                    (label_x, label_y),
                    (label_x + label_w, label_y + label_h),
                ],
                fill=color,
            )

            draw.text(
                (label_x + padding, label_y + padding),
                label,
                fill=(255, 255, 255),
                font=font,
            )

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def get_element_summary(self, elements: list[DOMElement]) -> str:
        """Create a text summary of interactive elements for the LLM.

        Format: "[index] tag: text (attributes)"
        """
        lines = []
        for el in elements:
            if not el.is_visible:
                continue

            parts = [f"[{el.index}] <{el.tag}>"]

            if el.text:
                parts.append(f'"{el.text[:80]}"')
            if el.aria_label:
                parts.append(f'aria="{el.aria_label[:50]}"')
            if el.placeholder:
                parts.append(f'placeholder="{el.placeholder[:50]}"')
            if el.attributes.get("href"):
                parts.append(f'href="{el.attributes["href"][:80]}"')
            if el.attributes.get("type"):
                parts.append(f'type="{el.attributes["type"]}"')

            lines.append(" ".join(parts))

        return "\n".join(lines)
