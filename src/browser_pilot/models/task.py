"""Task and sub-task data models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubTaskStatus(str, Enum):
    """Sub-task lifecycle states."""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskResult(BaseModel):
    """Final result of task execution."""

    success: bool = False
    summary: str = ""
    extracted_data: dict = Field(default_factory=dict)
    screenshots: list[str] = Field(default_factory=list)
    total_time: float = 0.0
    total_steps: int = 0
    errors: list[str] = Field(default_factory=list)


class SubTask(BaseModel):
    """Atomic sub-task within a larger task."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    order: int = 0
    status: SubTaskStatus = SubTaskStatus.PENDING
    actions_taken: list[str] = Field(default_factory=list)
    parent_task_id: str = ""
    error: Optional[str] = None


class Task(BaseModel):
    """Top-level task representation."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    instruction: str
    status: TaskStatus = TaskStatus.PENDING
    sub_tasks: list[SubTask] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    result: Optional[TaskResult] = None
    error: Optional[str] = None

    def mark_updated(self) -> None:
        """Update the timestamp."""
        self.updated_at = datetime.now(timezone.utc)
