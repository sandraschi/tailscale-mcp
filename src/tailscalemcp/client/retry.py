"""
Retry handler with exponential backoff for API requests.
"""

import asyncio
import random
from collections.abc import Callable
from typing import Any, TypeVar

import httpx
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class RetryHandler:
    """Handler for retrying failed API requests with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        """Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            jitter: Add random jitter to backoff delay
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def _should_retry(self, error: Exception) -> bool:
        """Determine if an error should be retried.

        Args:
            error: The exception that occurred

        Returns:
            True if the error should be retried
        """
        # Retry on network errors and 5xx status codes
        if isinstance(error, httpx.RequestError):
            return True

        # Retry on rate limit (429)
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            # Retry on rate limit, server errors, and gateway errors
            return status_code in (429, 500, 502, 503, 504)

        # Retry on timeout
        return isinstance(error, (httpx.TimeoutException, asyncio.TimeoutError))

    def _get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt.

        Args:
            attempt: Retry attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.backoff_factor**attempt

        if self.jitter:
            # Add random jitter (0-25% of delay)
            jitter_amount = delay * 0.25 * random.random()
            delay += jitter_amount

        return min(delay, 60.0)  # Cap at 60 seconds

    async def execute(
        self,
        func: Callable[[], Any],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute a function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            Exception: Last exception if all retries fail
        """
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            except Exception as e:
                last_error = e

                if not self._should_retry(e) or attempt >= self.max_retries:
                    # Don't retry or out of retries
                    logger.error(
                        "Request failed and won't be retried",
                        error=str(e),
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                    )
                    raise

                # Calculate delay and wait
                delay = self._get_delay(attempt)
                logger.warning(
                    "Request failed, retrying",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    delay=delay,
                )

                await asyncio.sleep(delay)

        # Should never reach here, but satisfy type checker
        if last_error:
            raise last_error

        raise RuntimeError("Retry handler failed unexpectedly")
