"""Template model for conversation templates."""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TemplateCategory(str, Enum):
    """Categories for conversation templates."""

    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    BRAINSTORM = "brainstorm"
    LEARNING = "learning"
    PRODUCTIVITY = "productivity"
    OTHER = "other"


class Template(Base):
    """Template model for conversation starters."""

    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="other")
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
