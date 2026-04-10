"""Rate limit configuration models."""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RateLimitTier(str, Enum):
    """Rate limit tiers."""

    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


# Default rate limits per tier
DEFAULT_LIMITS = {
    RateLimitTier.FREE: {
        "messages_per_minute": 5,
        "messages_per_day": 50,
        "conversations_per_day": 10,
        "images_per_day": 10,
        "api_calls_per_minute": 10,
    },
    RateLimitTier.PRO: {
        "messages_per_minute": 20,
        "messages_per_day": 500,
        "conversations_per_day": 100,
        "images_per_day": 100,
        "api_calls_per_minute": 30,
    },
    RateLimitTier.TEAM: {
        "messages_per_minute": 50,
        "messages_per_day": 2000,
        "conversations_per_day": 500,
        "images_per_day": 500,
        "api_calls_per_minute": 100,
    },
    RateLimitTier.ENTERPRISE: {
        "messages_per_minute": 200,
        "messages_per_day": 10000,
        "conversations_per_day": 2000,
        "images_per_day": 2000,
        "api_calls_per_minute": 500,
    },
}


class RateLimitConfig(Base):
    """Rate limit configuration for workspaces."""

    __tablename__ = "rate_limit_configs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    tier: Mapped[RateLimitTier] = mapped_column(String(20), default=RateLimitTier.FREE)
    custom_limits: Mapped[str | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class RateLimitUsage(Base):
    """Track rate limit usage per user/workspace."""

    __tablename__ = "rate_limit_usage"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )
    limit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)

    # Composite unique constraint
    __table_args__ = ({"sqlite_autoincrement": True},)
