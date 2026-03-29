"""FastAPI server schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    """Request to create a new task."""

    instruction: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Natural language task instruction",
    )
    provider: str = Field(
        default="ollama",
        description="LLM provider (ollama or openrouter)",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )


class TaskResponse(BaseModel):
    """Task status and result response."""

    id: str
    instruction: str
    status: str
    sub_tasks: list[dict] = Field(default_factory=list)
    result: dict | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Paginated task list."""

    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int


class StreamEvent(BaseModel):
    """Server-sent event data."""

    event: str
    task_id: str
    data: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"
    active_tasks: int = 0
    ollama_available: bool = False
    openrouter_available: bool = False


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
