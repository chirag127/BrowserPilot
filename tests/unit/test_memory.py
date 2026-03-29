"""Tests for agent memory."""

from browser_pilot.agent.memory import AgentMemory


class TestAgentMemory:
    """Test AgentMemory class."""

    def test_add_action(self) -> None:
        memory = AgentMemory()
        memory.add_action("clicked button")
        assert memory.action_count == 1
        assert memory.get_history() == ["clicked button"]

    def test_summarization(self) -> None:
        memory = AgentMemory(max_history=10, summarize_after=8)
        for i in range(20):
            memory.add_action(f"action {i}")

        # Should have summarized old actions
        full = memory.get_full_history()
        assert len(full) > 0
        # Total count preserved (20 actions added)
        assert memory.action_count == 20
        # Recent history capped at max_history
        assert len(memory.get_history()) <= 10

    def test_clear(self) -> None:
        memory = AgentMemory()
        memory.add_action("test")
        memory.add_observation({"key": "value"})
        memory.clear()
        assert memory.action_count == 0
        assert len(memory.get_observations()) == 0

    def test_observations(self) -> None:
        memory = AgentMemory()
        memory.add_observation({"page": "google.com"})
        obs = memory.get_observations()
        assert len(obs) == 1
        assert obs[0]["page"] == "google.com"
