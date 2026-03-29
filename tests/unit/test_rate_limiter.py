"""Tests for rate limiter."""

import asyncio

import pytest

from browser_pilot.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire(self) -> None:
        """Test basic acquire."""
        limiter = RateLimiter(rpm=100, daily_limit=1000)
        await limiter.acquire()
        assert limiter.remaining_rpm == 99
        assert limiter.remaining_daily == 999

    @pytest.mark.asyncio
    async def test_multiple_acquire(self) -> None:
        """Test multiple sequential acquisitions."""
        limiter = RateLimiter(rpm=100, daily_limit=1000)
        for _ in range(5):
            await limiter.acquire()
        assert limiter.remaining_rpm == 95
