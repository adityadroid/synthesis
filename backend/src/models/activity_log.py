"""Activity log model for audit trail."""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ActivityAction(str, Enum):
    """Types of auditable actions."""

    # Auth actions
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"
    PASSWORD_CHANGE = "password_change"

    # Conversation actions
    CONVERSATION_CREATE = "conversation_create"
    CONVERSATION_UPDATE = "conversation_update"
    CONVERSATION_DELETE = "conversation_delete"
    CONVERSATION_SHARE = "conversation_share"

    # Message actions
    MESSAGE_SEND = "message_send"
    MESSAGE_EDIT = "message_edit"
    MESSAGE_DELETE = "message_delete"

    # Workspace actions
    WORKSPACE_CREATE = "workspace_create"
    WORKSPACE_UPDATE = "workspace_update"
    WORKSPACE_DELETE = "workspace_delete"
    WORKSPACE_INVITE = "workspace_invite"
    WORKSPACE_JOIN = "workspace_join"
    WORKSPACE_LEAVE = "workspace_leave"

    # Admin actions
    USER_DELETE = "user_delete"
    SETTINGS_UPDATE = "settings_update"
    API_KEY_CREATE = "api_key_create"
    API_KEY_REVOKE = "api_key_revoke"

    # System actions
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"


class ActivityLog(Base):
    """Activity log for audit trail."""

    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )
    action: Mapped[ActivityAction] = mapped_column(
        SQLEnum(ActivityAction), nullable=False
    )
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_activity_user", "user_id", "created_at"),
        Index("idx_activity_workspace", "workspace_id", "created_at"),
        Index("idx_activity_action", "action", "created_at"),
        Index("idx_activity_created", "created_at"),
    )
