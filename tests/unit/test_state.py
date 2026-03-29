"""Tests for agent state machine."""

from browser_pilot.agent.state import AgentState, AgentStateMachine


class TestAgentStateMachine:
    """Test AgentStateMachine class."""

    def test_initial_state(self) -> None:
        """Test initial state is IDLE."""
        sm = AgentStateMachine()
        assert sm.current_state == AgentState.IDLE
        assert not sm.is_terminal
        assert not sm.is_failed

    def test_valid_transition(self) -> None:
        """Test valid state transition."""
        sm = AgentStateMachine()
        assert sm.transition(AgentState.PLANNING)
        assert sm.current_state == AgentState.PLANNING
        assert sm.previous_state == AgentState.IDLE

    def test_invalid_transition(self) -> None:
        """Test invalid state transition is rejected."""
        sm = AgentStateMachine()
        assert not sm.transition(AgentState.COMPLETED)
        assert sm.current_state == AgentState.IDLE

    def test_terminal_state(self) -> None:
        """Test terminal state detection."""
        sm = AgentStateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.DECIDING)
        sm.transition(AgentState.GROUNDING)
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.COMPLETED)
        assert sm.is_terminal

    def test_failure_state(self) -> None:
        """Test failure state."""
        sm = AgentStateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.FAILED)
        assert sm.is_failed
        assert sm.is_terminal

    def test_step_counter(self) -> None:
        """Test step counting on EXECUTING transitions."""
        sm = AgentStateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.EXECUTING)
        assert sm.step_count == 1
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.DECIDING)
        sm.transition(AgentState.GROUNDING)
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.DECIDING)
        sm.transition(AgentState.GROUNDING)
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.VALIDATING)
        sm.transition(AgentState.EXECUTING)
        assert sm.step_count == 2

    def test_failure_counter(self) -> None:
        """Test failure counting."""
        sm = AgentStateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.EXECUTING)
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.DECIDING)
        sm.transition(AgentState.GROUNDING)
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.RECOVERING)
        assert sm.failure_count == 1
