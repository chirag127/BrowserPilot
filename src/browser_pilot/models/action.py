"""Action data models."""

from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of browser actions."""

    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    SELECT = "select"
    HOVER = "hover"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    GO_BACK = "go_back"
    PRESS_KEY = "press_key"
    DRAG_AND_DROP = "drag_and_drop"
    UPLOAD_FILE = "upload_file"


class ActionStatus(str, Enum):
    """Action execution status."""

    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"


class Action(BaseModel):
    """Single browser action with context."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ActionType
    params: dict = Field(default_factory=dict)
    target_element_index: Optional[int] = None
    status: ActionStatus = ActionStatus.PENDING
    confidence: float = 0.0
    reasoning: str = ""
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    error: Optional[str] = None
    step_number: int = 0
