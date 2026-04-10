"""Rate limit service for managing API quotas."""

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from ..models.rate_limit import (
    RateLimitConfig,
    RateLimitUsage,
    RateLimitTier,
    DEFAULT_LIMITS,
)


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception."""

    def __init__(self, limit_type: str, limit: int, reset_at: datetime):
        self.limit_type = limit_type
        self.limit = limit
        self.reset_at = reset_at
        super().__init__(f"Rate limit exceeded for {limit_type}: {limit} per window")


class RateLimitService:
    """Service for checking and enforcing rate limits."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_limits(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> dict:
        """Get rate limits for user/workspace."""
        # Check for custom config
        query = select(RateLimitConfig).where(RateLimitConfig.is_active == True)

        if workspace_id:
            query = query.where(RateLimitConfig.workspace_id == workspace_id)
        elif user_id:
            query = query.where(RateLimitConfig.user_id == user_id)

        result = await self.db.execute(query)
        config = result.scalar_one_or_none()

        if config:
            if config.custom_limits:
                return config.custom_limits
            return DEFAULT_LIMITS.get(config.tier, DEFAULT_LIMITS[RateLimitTier.FREE])

        # Default limits for free tier
        return DEFAULT_LIMITS[RateLimitTier.FREE]

    async def check_rate_limit(
        self,
        limit_type: str,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> bool:
        """Check if action is within rate limit. Returns True if allowed."""
        limits = await self.get_limits(user_id, workspace_id)

        if limit_type not in limits:
            return True  # Unknown limit type, allow

        limit = limits[limit_type]
        if limit == 0:
            return True  # Unlimited

        window = self._get_window_for_limit_type(limit_type)
        current_count = await self._get_usage(limit_type, user_id, workspace_id, window)

        return current_count < limit

    async def record_usage(
        self,
        limit_type: str,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ):
        """Record an action for rate limiting."""
        window = self._get_window_for_limit_type(limit_type)
        window_start = self._get_window_start(window)

        # Check existing usage record
        result = await self.db.execute(
            select(RateLimitUsage).where(
                and_(
                    RateLimitUsage.user_id == user_id,
                    RateLimitUsage.workspace_id == workspace_id,
                    RateLimitUsage.limit_type == limit_type,
                    RateLimitUsage.window_start == window_start,
                )
            )
        )
        usage = result.scalar_one_or_none()

        if usage:
            usage.count += 1
        else:
            usage = RateLimitUsage(
                id=None,  # Let SQLAlchemy generate
                user_id=user_id,
                workspace_id=workspace_id,
                limit_type=limit_type,
                window_start=window_start,
                count=1,
            )
            self.db.add(usage)

        await self.db.flush()

    async def enforce_rate_limit(
        self,
        limit_type: str,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ):
        """Enforce rate limit, raise exception if exceeded."""
        allowed = await self.check_rate_limit(limit_type, user_id, workspace_id)

        if not allowed:
            limits = await self.get_limits(user_id, workspace_id)
            limit = limits.get(limit_type, 0)
            window = self._get_window_for_limit_type(limit_type)
            reset_at = datetime.utcnow() + window
            raise RateLimitExceeded(limit_type, limit, reset_at)

        await self.record_usage(limit_type, user_id, workspace_id)

    async def get_usage_stats(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> dict:
        """Get current usage statistics."""
        limits = await self.get_limits(user_id, workspace_id)
        stats = {}

        for limit_type, limit in limits.items():
            window = self._get_window_for_limit_type(limit_type)
            window_start = self._get_window_start(window)
            count = await self._get_usage(limit_type, user_id, workspace_id, window)

            stats[limit_type] = {
                "used": count,
                "limit": limit,
                "remaining": max(0, limit - count),
                "window": window.total_seconds() / 60,  # In minutes
                "reset_at": (window_start + window).isoformat(),
            }

        return stats

    async def cleanup_old_usage(self, days: int = 7):
        """Clean up old usage records."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        await self.db.execute(
            delete(RateLimitUsage).where(RateLimitUsage.window_start < cutoff)
        )
        await self.db.flush()

    def _get_window_for_limit_type(self, limit_type: str) -> timedelta:
        """Get the time window for a limit type."""
        if "minute" in limit_type:
            return timedelta(minutes=1)
        elif "hour" in limit_type:
            return timedelta(hours=1)
        elif "day" in limit_type:
            return timedelta(days=1)
        else:
            return timedelta(minutes=1)  # Default

    def _get_window_start(self, window: timedelta) -> datetime:
        """Get the start of the current window."""
        now = datetime.utcnow()
        if window == timedelta(days=1):
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif window == timedelta(hours=1):
            return now.replace(minute=0, second=0, microsecond=0)
        else:
            return now.replace(second=0, microsecond=0)

    async def _get_usage(
        self,
        limit_type: str,
        user_id: str | None,
        workspace_id: str | None,
        window: timedelta,
    ) -> int:
        """Get current usage count for a limit type."""
        window_start = self._get_window_start(window)

        result = await self.db.execute(
            select(RateLimitUsage).where(
                and_(
                    RateLimitUsage.user_id == user_id,
                    RateLimitUsage.workspace_id == workspace_id,
                    RateLimitUsage.limit_type == limit_type,
                    RateLimitUsage.window_start == window_start,
                )
            )
        )
        usage = result.scalar_one_or_none()

        return usage.count if usage else 0
