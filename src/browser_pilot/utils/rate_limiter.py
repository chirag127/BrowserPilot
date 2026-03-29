"""API rate limiter for LLM providers."""

import asyncio
import time
from collections import deque

from browser_pilot.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls.

    Enforces per-minute and per-day request limits.
    """

    def __init__(
        self,
        rpm: int = 10,
        daily_limit: int = 250,
    ) -> None:
        self._rpm = rpm
        self._daily_limit = daily_limit
        self._minute_requests: deque[float] = deque()
        self._daily_count = 0
        self._daily_reset = time.time() + 86400
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request slot is available."""
        async with self._lock:
            now = time.time()

            # Reset daily counter
            if now > self._daily_reset:
                self._daily_count = 0
                self._daily_reset = now + 86400

            # Check daily limit
            if self._daily_count >= self._daily_limit:
                wait = self._daily_reset - now
                logger.warning(
                    "daily_limit_reached",
                    remaining_seconds=wait,
                )
                await asyncio.sleep(min(wait, 60))

            # Clean old minute entries
            while self._minute_requests and now - self._minute_requests[0] > 60:
                self._minute_requests.popleft()

            # Check RPM
            if len(self._minute_requests) >= self._rpm:
                wait = 60 - (now - self._minute_requests[0]) + 0.1
                logger.warning("rpm_limit_reached", wait_seconds=wait)
                await asyncio.sleep(max(0, wait))

            self._minute_requests.append(now)
            self._daily_count += 1

    @property
    def remaining_rpm(self) -> int:
        """Remaining requests this minute."""
        now = time.time()
        while self._minute_requests and now - self._minute_requests[0] > 60:
            self._minute_requests.popleft()
        return max(0, self._rpm - len(self._minute_requests))

    @property
    def remaining_daily(self) -> int:
        """Remaining requests today."""
        return max(0, self._daily_limit - self._daily_count)
