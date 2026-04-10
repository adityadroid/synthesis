"""Custom model registry for fine-tuned and custom models."""

import uuid
import json
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ModelType(str, Enum):
    """Types of custom models."""

    FINE_TUNED = "fine_tuned"
    CUSTOM = "custom"
    LLAMA_CPP = "llama_cpp"
    OTHER = "other"


class CustomModel(Base):
    """Custom model configuration."""

    __tablename__ = "custom_models"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    workspace_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=True
    )

    # Model info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_type: Mapped[ModelType] = mapped_column(String(20), default=ModelType.CUSTOM)

    # Endpoint configuration
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Model capabilities
    capabilities: Mapped[str] = mapped_column(
        JSON, default=dict
    )  # {vision: bool, streaming: bool, function_calling: bool}

    # Pricing
    cost_per_1k_input: Mapped[float] = mapped_column(default=0.0)
    cost_per_1k_output: Mapped[float] = mapped_column(default=0.0)

    # Performance tracking
    request_count: Mapped[int] = mapped_column(default=0)
    total_tokens: Mapped[int] = mapped_column(default=0)
    avg_latency_ms: Mapped[float] = mapped_column(default=0.0)
    error_count: Mapped[int] = mapped_column(default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # A/B testing
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_ab_test_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    ab_test_weight: Mapped[float] = mapped_column(
        default=0.5
    )  # 0.0-1.0 for traffic split

    # Metadata
    metadata: Mapped[str | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class ModelUsageLog(Base):
    """Log of custom model usage for analytics."""

    __tablename__ = "model_usage_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("custom_models.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # Request details
    input_tokens: Mapped[int] = mapped_column(default=0)
    output_tokens: Mapped[int] = mapped_column(default=0)
    latency_ms: Mapped[float] = mapped_column(default=0.0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cost
    cost: Mapped[float] = mapped_column(default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
