"""API Key model for programmatic access."""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class APIKeyScope(str, Enum):
    """API key permission scopes."""

    # Chat permissions
    CHAT_READ = "chat:read"
    CHAT_WRITE = "chat:write"
    CHAT_DELETE = "chat:delete"

    # Conversation permissions
    CONVERSATION_READ = "conversation:read"
    CONVERSATION_WRITE = "conversation:write"

    # User permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"

    # Admin permissions
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"


# Default scopes for new keys
DEFAULT_SCOPES = [
    APIKeyScope.CHAT_READ,
    APIKeyScope.CHAT_WRITE,
    APIKeyScope.CONVERSATION_READ,
    APIKeyScope.CONVERSATION_WRITE,
]


class APIKey(Base):
    """User API keys for programmatic access."""

    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Key hash (never store the actual key)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    key_prefix: Mapped[str] = mapped_column(
        String(8), nullable=False
    )  # First 8 chars for identification

    scopes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of scopes
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Usage tracking
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    request_count: Mapped[int] = mapped_column(default=0)

    # Expiration
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_key() -> tuple[str, str]:
        """Generate a new API key and its hash.

        Returns:
            Tuple of (raw_key, key_hash)
            The raw_key should be shown to user once and never stored.
        """
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]
        return raw_key, key_hash, key_prefix

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Hash a raw API key for verification."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def verify_key(self, raw_key: str) -> bool:
        """Verify a raw key against its hash."""
        return self.key_hash == self.hash_key(raw_key)

    def is_expired(self) -> bool:
        """Check if the key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if key has a specific scope."""
        import json

        scopes = json.loads(self.scopes)
        return scope.value in scopes

    def get_scopes(self) -> list[str]:
        """Get list of scopes."""
        import json

        return json.loads(self.scopes)
