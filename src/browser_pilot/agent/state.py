"""Agent state machine."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from browser_pilot.logging import get_logger

logger = get_logger(__name__)


class AgentState(str, Enum):
    """Agent lifecycle states."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    OBSERVING = "observing"
    DECIDING = "deciding"
    GROUNDING = "grounding"
    ACTING = "acting"
    VALIDATING = "validating"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStateMachine(BaseModel):
    """Finite state machine for agent lifecycle."""

    current_state: AgentState = AgentState.IDLE
    previous_state: Optional[AgentState] = None
    step_count: int = 0
    failure_count: int = 0
    last_transition: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_error: Optional[str] = None

    # Valid state transitions
    TRANSITIONS: dict = {
        AgentState.IDLE: [AgentState.PLANNING, AgentState.CANCELLED],
        AgentState.PLANNING: [
            AgentState.EXECUTING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.EXECUTING: [
            AgentState.OBSERVING,
            AgentState.VALIDATING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.OBSERVING: [
            AgentState.DECIDING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.DECIDING: [
            AgentState.GROUNDING,
            AgentState.OBSERVING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.GROUNDING: [
            AgentState.ACTING,
            AgentState.DECIDING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.ACTING: [
            AgentState.OBSERVING,
            AgentState.RECOVERING,
            AgentState.VALIDATING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.RECOVERING: [
            AgentState.OBSERVING,
            AgentState.VALIDATING,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
        AgentState.VALIDATING: [
            AgentState.EXECUTING,
            AgentState.COMPLETED,
            AgentState.FAILED,
            AgentState.CANCELLED,
        ],
    }

    def transition(self, new_state: AgentState) -> bool:
        """Attempt a state transition.

        Returns True if the transition was valid and applied.
        """
        valid = self.TRANSITIONS.get(self.current_state, [])
        if new_state not in valid:
            logger.warning(
                "invalid_transition",
                from_state=self.current_state.value,
                to_state=new_state.value,
                valid=[s.value for s in valid],
            )
            return False

        self.previous_state = self.current_state
        self.current_state = new_state
        self.last_transition = datetime.now(timezone.utc)

        if new_state == AgentState.EXECUTING:
            self.step_count += 1
        elif new_state == AgentState.RECOVERING:
            self.failure_count += 1

        logger.info(
            "state_transition",
            from_state=self.previous_state.value,
            to_state=new_state.value,
            step=self.step_count,
            failures=self.failure_count,
        )
        return True

    @property
    def is_terminal(self) -> bool:
        """Check if the current state is terminal."""
        return self.current_state in (
            AgentState.COMPLETED,
            AgentState.FAILED,
            AgentState.CANCELLED,
        )

    @property
    def is_failed(self) -> bool:
        """Check if the agent has failed."""
        return self.current_state == AgentState.FAILED
