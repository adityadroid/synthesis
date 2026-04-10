"""Rate limiting middleware using token bucket algorithm."""

import time
from collections import defaultdict
from typing import Callable
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10


class TokenBucket:
    """Token bucket algorithm implementation."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # Tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now

    def get_wait_time(self) -> float:
        """Get time to wait before a token is available."""
        if self.tokens >= 1:
            return 0.0
        return (1 - self.tokens) / self.rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
    ):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self._buckets: dict[str, dict[str, TokenBucket]] = defaultdict(dict)

    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Get identifier for rate limiting
        identifier = self._get_identifier(request)

        # Check rate limits
        if not self._check_rate_limit(identifier):
            retry_after = self._get_retry_after(identifier)
            logger.warning(
                "Rate limit exceeded",
                identifier=identifier[:8] if identifier else "unknown",
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(int(retry_after)),
                    "X-RateLimit-Limit": str(self.config.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = self._get_remaining(identifier)
        response.headers["X-RateLimit-Limit"] = str(self.config.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response

    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting (IP or user)."""
        # Try to get user ID from request state
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit."""
        # Get or create buckets for this identifier
        if identifier not in self._buckets:
            self._buckets[identifier] = {
                "minute": TokenBucket(
                    rate=self.config.requests_per_minute / 60,
                    capacity=self.config.burst_size,
                ),
                "hour": TokenBucket(
                    rate=self.config.requests_per_hour / 3600,
                    capacity=self.config.requests_per_hour,
                ),
                "day": TokenBucket(
                    rate=self.config.requests_per_day / 86400,
                    capacity=self.config.requests_per_day,
                ),
            }

        buckets = self._buckets[identifier]

        # Check minute bucket first (most restrictive)
        return buckets["minute"].consume()

    def _get_retry_after(self, identifier: str) -> float:
        """Get seconds until a request can be made."""
        if identifier in self._buckets:
            return self._buckets[identifier]["minute"].get_wait_time()
        return 60.0

    def _get_remaining(self, identifier: str) -> int:
        """Get remaining requests in current window."""
        if identifier in self._buckets:
            tokens = int(self._buckets[identifier]["minute"].tokens)
            return max(0, tokens)
        return self.config.burst_size


def get_rate_limit_headers(
    requests_per_minute: int,
    remaining: int,
    reset_time: int,
) -> dict:
    """Generate rate limit response headers."""
    return {
        "X-RateLimit-Limit": str(requests_per_minute),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time),
    }
