"""Shared test fixtures."""

from pathlib import Path

import pytest

from browser_pilot.models.action import Action, ActionType
from browser_pilot.models.dom import BoundingBox, DOMElement
from browser_pilot.models.task import SubTask, Task, TaskStatus


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="test-task-001",
        instruction="Go to example.com and extract the page title",
        status=TaskStatus.PENDING,
        sub_tasks=[
            SubTask(
                description="Navigate to example.com",
                order=0,
                parent_task_id="test-task-001",
            ),
            SubTask(
                description="Extract the page title",
                order=1,
                parent_task_id="test-task-001",
            ),
        ],
    )


@pytest.fixture
def sample_action() -> Action:
    """Create a sample action for testing."""
    return Action(
        id="test-action-001",
        action_type=ActionType.CLICK,
        target_element_index=3,
        confidence=0.9,
        reasoning="Clicking the search button",
    )


@pytest.fixture
def sample_elements() -> list[DOMElement]:
    """Create sample DOM elements for testing."""
    return [
        DOMElement(
            index=0,
            tag="a",
            text="Home",
            attributes={"href": "/"},
            bbox=BoundingBox(x=10, y=10, width=50, height=20),
            is_interactive=True,
            is_visible=True,
            selector="a[href='/']",
        ),
        DOMElement(
            index=1,
            tag="input",
            text="",
            attributes={"type": "text", "name": "q"},
            bbox=BoundingBox(x=100, y=10, width=300, height=30),
            is_interactive=True,
            is_visible=True,
            selector="input[name='q']",
            placeholder="Search...",
        ),
        DOMElement(
            index=2,
            tag="button",
            text="Search",
            attributes={"type": "submit"},
            bbox=BoundingBox(x=410, y=10, width=80, height=30),
            is_interactive=True,
            is_visible=True,
            selector="button[type='submit']",
        ),
    ]


@pytest.fixture
def mock_llm_response() -> str:
    """Create a mock LLM response."""
    return """{
        "action": "click",
        "element_index": 2,
        "params": {},
        "confidence": 0.95,
        "reasoning": "Clicking the search button to submit"
    }"""


@pytest.fixture
def tmp_screenshot_dir(tmp_path: Path) -> Path:
    """Create temporary screenshot directory."""
    d = tmp_path / "screenshots"
    d.mkdir()
    return d
