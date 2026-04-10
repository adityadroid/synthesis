"""Retry logic with exponential backoff and circuit breaker."""

import asyncio
import time
from typing import TypeVar, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

from .logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on: tuple = (Exception,)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_requests: int = 3


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(self, config: CircuitBreakerConfig | None = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.half_open_attempts = 0

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.half_open_requests:
                self._transition_to(CircuitState.CLOSED)
                logger.info(
                    "Circuit breaker closed after recovery", state=self.state.value
                )

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
            logger.warning("Circuit breaker opened after half-open failure")
        elif self.failure_count >= self.config.failure_threshold:
            self._transition_to(CircuitState.OPEN)
            logger.warning(
                "Circuit breaker opened",
                failure_count=self.failure_count,
                threshold=self.config.failure_threshold,
            )

    def can_attempt(self) -> bool:
        """Check if a request can be attempted."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self._transition_to(CircuitState.HALF_OPEN)
                return True
            return False

        return True  # HALF_OPEN

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        self.state = new_state
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.half_open_attempts += 1
            self.success_count = 0


async def retry_with_backoff(
    func: Callable[..., Any],
    config: RetryConfig | None = None,
    circuit_breaker: CircuitBreaker | None = None,
) -> Any:
    """Execute a function with retry logic and optional circuit breaker."""
    config = config or RetryConfig()

    if circuit_breaker and not circuit_breaker.can_attempt():
        raise CircuitBreakerOpen("Circuit breaker is open")

    last_exception: Exception | None = None

    for attempt in range(config.max_attempts):
        try:
            result = await func() if asyncio.iscoroutinefunction(func) else func()

            if circuit_breaker:
                circuit_breaker.record_success()

            return result

        except config.retry_on as e:
            last_exception = e
            logger.warning(
                "Retryable error occurred",
                attempt=attempt + 1,
                max_attempts=config.max_attempts,
                error=str(e),
            )

            if attempt < config.max_attempts - 1:
                delay = _calculate_delay(config, attempt)
                logger.info("Retrying after delay", delay_seconds=delay)
                await asyncio.sleep(delay)
            else:
                if circuit_breaker:
                    circuit_breaker.record_failure()
                raise

        except Exception as e:
            logger.error("Non-retryable error", error=str(e))
            raise

    if last_exception:
        raise last_exception


def _calculate_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate delay with exponential backoff and optional jitter."""
    delay = config.base_delay * (config.exponential_base**attempt)
    delay = min(delay, config.max_delay)

    if config.jitter:
        import random

        delay *= 0.5 + random.random()  # 50-150% of calculated delay

    return delay


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""

    pass


def with_retry(config: RetryConfig | None = None):
    """Decorator for adding retry logic to async functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_with_backoff(
                lambda: func(*args, **kwargs),
                config=config,
            )

        return wrapper

    return decorator


def with_circuit_breaker(config: CircuitBreakerConfig | None = None):
    """Decorator for adding circuit breaker to async functions."""
    breaker = CircuitBreaker(config)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not breaker.can_attempt():
                raise CircuitBreakerOpen("Circuit breaker is open")
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise

        return wrapper

    return decorator
