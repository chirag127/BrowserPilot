"""Execution result models."""

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class StepResult(BaseModel):
    """Result of a single execution step."""

    step_number: int
    action_type: str
    action_params: dict = Field(default_factory=dict)
    success: bool = False
    confidence: float = 0.0
    reasoning: str = ""
    screenshot_path: str | None = None
    error: str | None = None
    elapsed_seconds: float = 0.0
    extracted_data: dict = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Aggregate result of a full execution run."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    instruction: str
    success: bool = False
    summary: str = ""
    steps: list[StepResult] = Field(default_factory=list)
    extracted_data: dict = Field(default_factory=dict)
    screenshots: list[str] = Field(default_factory=list)
    total_time: float = 0.0
    total_steps: int = 0
    errors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
