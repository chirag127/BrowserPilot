"""Tests for data models."""

from browser_pilot.models.action import Action, ActionStatus, ActionType
from browser_pilot.models.dom import BoundingBox
from browser_pilot.models.task import SubTask, SubTaskStatus, Task, TaskStatus


class TestTask:
    """Test Task model."""

    def test_task_creation(self) -> None:
        """Test basic task creation."""
        task = Task(instruction="Test task")
        assert task.status == TaskStatus.PENDING
        assert task.id is not None
        assert len(task.sub_tasks) == 0

    def test_task_with_sub_tasks(self, sample_task: Task) -> None:
        """Test task with sub-tasks."""
        assert len(sample_task.sub_tasks) == 2
        assert sample_task.sub_tasks[0].order == 0
        assert sample_task.sub_tasks[1].order == 1

    def test_mark_updated(self) -> None:
        """Test mark_updated updates timestamp."""
        task = Task(instruction="Test")
        old = task.updated_at
        task.mark_updated()
        assert task.updated_at >= old


class TestSubTask:
    """Test SubTask model."""

    def test_sub_task_defaults(self) -> None:
        """Test default sub-task values."""
        st = SubTask(description="Do something")
        assert st.status == SubTaskStatus.PENDING
        assert st.id is not None
        assert len(st.actions_taken) == 0


class TestAction:
    """Test Action model."""

    def test_action_creation(self, sample_action: Action) -> None:
        """Test action creation."""
        assert sample_action.action_type == ActionType.CLICK
        assert sample_action.target_element_index == 3
        assert sample_action.confidence == 0.9

    def test_action_status_default(self) -> None:
        """Test default action status."""
        action = Action(action_type=ActionType.TYPE)
        assert action.status == ActionStatus.PENDING


class TestDOMElement:
    """Test DOMElement model."""

    def test_element_creation(self, sample_elements) -> None:
        """Test DOM element creation."""
        el = sample_elements[0]
        assert el.index == 0
        assert el.tag == "a"
        assert el.is_interactive

    def test_bounding_box(self) -> None:
        """Test bounding box."""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        assert bbox.x == 10
        assert bbox.width == 100
