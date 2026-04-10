"""Data retention policy models for compliance."""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RetentionPeriod(str, Enum):
    """Standard retention periods."""

    DAYS_30 = "30_days"
    DAYS_90 = "90_days"
    DAYS_180 = "180_days"
    DAYS_365 = "365_days"
    YEARS_2 = "2_years"
    YEARS_5 = "5_years"
    FOREVER = "forever"


class DataType(str, Enum):
    """Types of data that can have retention policies."""

    CONVERSATIONS = "conversations"
    MESSAGES = "messages"
    USER_DATA = "user_data"
    ACTIVITY_LOGS = "activity_logs"
    USAGE_DATA = "usage_data"
    API_LOGS = "api_logs"


class RetentionPolicy(Base):
    """Data retention policy configuration."""

    __tablename__ = "retention_policies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Policy configuration
    data_type: Mapped[DataType] = mapped_column(String(30), nullable=False)
    retention_period: Mapped[RetentionPeriod] = mapped_column(
        String(20), nullable=False
    )

    # Legal hold
    is_legal_hold: Mapped[bool] = mapped_column(Boolean, default=False)
    legal_hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Auto-delete settings
    auto_delete_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    deletion_schedule: Mapped[str] = mapped_column(
        String(50), default="daily"
    )  # daily, weekly, monthly

    # Export before delete
    export_before_delete: Mapped[bool] = mapped_column(Boolean, default=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Tracking
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    records_deleted: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get_retention_days(self) -> int | None:
        """Get retention period in days."""
        days_map = {
            RetentionPeriod.DAYS_30: 30,
            RetentionPeriod.DAYS_90: 90,
            RetentionPeriod.DAYS_180: 180,
            RetentionPeriod.DAYS_365: 365,
            RetentionPeriod.YEARS_2: 730,
            RetentionPeriod.YEARS_5: 1825,
            RetentionPeriod.FOREVER: None,
        }
        return days_map.get(self.retention_period)


class DeletionLog(Base):
    """Log of data deletions for compliance audit."""

    __tablename__ = "deletion_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    policy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("retention_policies.id"), nullable=False
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )

    # Deletion details
    data_type: Mapped[DataType] = mapped_column(String(30), nullable=False)
    records_deleted: Mapped[int] = mapped_column(Integer, default=0)
    export_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )  # Reference to export

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="completed"
    )  # pending, completed, failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Compliance
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
