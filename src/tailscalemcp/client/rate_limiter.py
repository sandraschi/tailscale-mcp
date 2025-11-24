"""
Rate limiter for Tailscale API calls.

Implements token bucket algorithm to respect API rate limits.
"""

import asyncio
import time
from collections import deque
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(
        self,
        rate: float = 1.0,
        window: int = 60,
    ) -> None:
        """Initialize rate limiter.

        Args:
            rate: Requests per second allowed
            window: Time window in seconds for tracking
        """
        self.rate = rate
        self.window = window
        self.min_interval = 1.0 / rate if rate > 0 else 0
        self._last_request_time = 0.0
        self._request_times: deque[float] = deque(maxlen=int(rate * window))
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request.

        Waits if necessary to respect rate limits.
        """
        async with self._lock:
            current_time = time.monotonic()

            # Remove old requests outside the window
            cutoff_time = current_time - self.window
            while self._request_times and self._request_times[0] < cutoff_time:
                self._request_times.popleft()

            # Check if we're at the rate limit
            if len(self._request_times) >= int(self.rate * self.window):
                # Wait until oldest request is outside the window
                wait_time = self._request_times[0] + self.window - current_time
                if wait_time > 0:
                    logger.debug(
                        "Rate limit reached, waiting",
                        wait_time=wait_time,
                        rate=self.rate,
                    )
                    await asyncio.sleep(wait_time)
                    current_time = time.monotonic()

            # Ensure minimum interval between requests
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.debug("Enforcing minimum interval", sleep_time=sleep_time)
                await asyncio.sleep(sleep_time)
                current_time = time.monotonic()

            # Record this request
            self._last_request_time = current_time
            self._request_times.append(current_time)

    def get_stats(self) -> dict[str, Any]:
        """Get current rate limiter statistics.

        Returns:
            Dictionary with rate limit stats
        """
        current_time = time.monotonic()
        cutoff_time = current_time - self.window
        recent_requests = [
            req_time for req_time in self._request_times if req_time >= cutoff_time
        ]

        return {
            "rate": self.rate,
            "window": self.window,
            "requests_in_window": len(recent_requests),
            "max_requests": int(self.rate * self.window),
            "min_interval": self.min_interval,
        }
