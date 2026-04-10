"""Message model."""

import json
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, MessageRole


class Message(Base):
    """Message model for chat messages."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    images: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of image URLs
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def get_images(self) -> list[dict]:
        """Parse images JSON to list."""
        if not self.images:
            return []
        return json.loads(self.images)

    def set_images(self, images: list[dict]) -> None:
        """Set images from list of dicts."""
        self.images = json.dumps(images) if images else None
