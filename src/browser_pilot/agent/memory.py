"""Agent memory — context management and token budgeting."""

from browser_pilot.logging import get_logger

logger = get_logger(__name__)


class AgentMemory:
    """Manages agent context including action history and observations.

    Implements a sliding window approach to keep token usage bounded.
    """

    def __init__(
        self, max_history: int = 20, summarize_after: int = 15
    ) -> None:
        self._history: list[str] = []
        self._observations: list[dict] = []
        self._summaries: list[str] = []
        self._max_history = max_history
        self._summarize_after = summarize_after

    def add_action(self, action_desc: str) -> None:
        """Add an action to the history."""
        self._history.append(action_desc)
        self._maybe_summarize()

    def add_observation(self, observation: dict) -> None:
        """Store a key observation."""
        self._observations.append(observation)

    def get_history(self) -> list[str]:
        """Get the action history (recent actions only)."""
        return self._history[-self._max_history :]

    def get_full_history(self) -> list[str]:
        """Get all actions including summarized older ones."""
        return self._summaries + self._history[-self._max_history :]

    def get_observations(self) -> list[dict]:
        """Get stored observations."""
        return self._observations[-10:]

    def _maybe_summarize(self) -> None:
        """Summarize old history to save tokens."""
        if len(self._history) > self._summarize_after:
            old = self._history[:5]
            summary = (
                f"[Summary of {len(old)} earlier actions: "
                + "; ".join(a[:50] for a in old)
                + "]"
            )
            self._summaries.append(summary)
            self._history = self._history[5:]
            logger.info(
                "history_summarized",
                summarized_count=len(old),
                remaining=len(self._history),
            )

    def clear(self) -> None:
        """Clear all memory."""
        self._history.clear()
        self._observations.clear()
        self._summaries.clear()

    @property
    def action_count(self) -> int:
        """Total number of actions taken."""
        return len(self._history) + len(self._summaries)
