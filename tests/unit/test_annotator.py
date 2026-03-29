"""Tests for DOM annotator."""

from browser_pilot.models.dom import BoundingBox, DOMElement
from browser_pilot.vision.annotator import DOMAnnotator


class TestDOMAnnotator:
    """Test DOMAnnotator class."""

    def test_element_summary(self, sample_elements) -> None:
        """Test element summary generation."""
        annotator = DOMAnnotator()
        summary = annotator.get_element_summary(sample_elements)
        assert "[0]" in summary
        assert "Home" in summary
        assert "[1]" in summary
        assert "[2]" in summary

    def test_empty_elements(self) -> None:
        """Test summary with no elements."""
        annotator = DOMAnnotator()
        summary = annotator.get_element_summary([])
        assert summary == ""

    def test_hidden_elements_excluded(self) -> None:
        """Test hidden elements are excluded from summary."""
        annotator = DOMAnnotator()
        elements = [
            DOMElement(
                index=0,
                tag="button",
                text="Visible",
                is_visible=True,
            ),
            DOMElement(
                index=1,
                tag="button",
                text="Hidden",
                is_visible=False,
            ),
        ]
        summary = annotator.get_element_summary(elements)
        assert "Visible" in summary
        assert "Hidden" not in summary
