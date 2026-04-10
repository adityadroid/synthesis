"""SSO/SAML configuration models for enterprise authentication."""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SSOProvider(str, Enum):
    """Supported SSO providers."""

    SAML = "saml"
    OKTA = "okta"
    AZURE_AD = "azure_ad"
    GOOGLE = "google_workspace"
    GENERIC_SAML = "generic_saml"


class SSOConfig(Base):
    """SSO configuration for workspaces."""

    __tablename__ = "sso_configs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False
    )

    # Provider configuration
    provider: Mapped[SSOProvider] = mapped_column(String(20), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # SAML settings
    entity_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sso_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    slo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    x509_cert: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Okta/Azure AD specific
    client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Role mapping from IdP
    role_mapping: Mapped[str | None] = mapped_column(
        JSON, nullable=True
    )  # {"admin": ["admin@company.com"], "member": []}
    auto_provision_users: Mapped[bool] = mapped_column(Boolean, default=True)

    # JIT provisioning
    jit_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    default_role: Mapped[str] = mapped_column(String(20), default="member")

    # Metadata
    metadata_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_xml: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tracking
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    login_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SSOSession(Base):
    """SSO session tracking."""

    __tablename__ = "sso_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    sso_config_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sso_configs.id"), nullable=False
    )

    # Session info
    name_id: Mapped[str] = mapped_column(String(255), nullable=True)
    session_index: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Expiration
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
