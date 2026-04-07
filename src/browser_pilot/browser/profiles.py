"""Browser profile management for session persistence."""

import json
from pathlib import Path

from browser_pilot.logging import get_logger

logger = get_logger(__name__)


class BrowserProfile:
    """Manages browser profiles with cookie and storage persistence."""

    def __init__(self, profile_dir: Path) -> None:
        self._profile_dir = profile_dir
        self._profile_dir.mkdir(parents=True, exist_ok=True)

    @property
    def storage_state_path(self) -> Path:
        """Path to the storage state JSON file."""
        return self._profile_dir / "storage_state.json"

    @property
    def cookies_path(self) -> Path:
        """Path to the cookies JSON file."""
        return self._profile_dir / "cookies.json"

    def save_storage_state(self, state: dict) -> None:
        """Save browser storage state (cookies, localStorage)."""
        with open(self.storage_state_path, "w") as f:
            json.dump(state, f, indent=2)
        logger.info("storage_state_saved", path=str(self.storage_state_path))

    def load_storage_state(self) -> dict | None:
        """Load browser storage state if it exists."""
        if self.storage_state_path.exists():
            with open(self.storage_state_path) as f:
                state = json.load(f)
            logger.info("storage_state_loaded", path=str(self.storage_state_path))
            return state
        return None

    def clear(self) -> None:
        """Clear all profile data."""
        if self.storage_state_path.exists():
            self.storage_state_path.unlink()
        if self.cookies_path.exists():
            self.cookies_path.unlink()
        logger.info("profile_cleared", dir=str(self._profile_dir))
