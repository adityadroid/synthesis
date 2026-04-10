"""SSO/SAML routes for enterprise authentication."""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_db
from ..models.sso import SSOConfig, SSOProvider, SSOSession
from ..models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from ..models.user import User
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/sso", tags=["sso"])


class SSOConfigResponse(BaseModel):
    """SSO configuration response."""

    id: str
    workspace_id: str
    provider: str
    is_enabled: bool
    entity_id: str | None
    sso_url: str | None
    auto_provision_users: bool
    jit_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SSOConfigCreate(BaseModel):
    """Request to create SSO configuration."""

    workspace_id: str
    provider: str
    entity_id: str | None = None
    sso_url: str | None = None
    x509_cert: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    role_mapping: dict | None = None
    auto_provision_users: bool = True
    jit_enabled: bool = True


class SSOConfigUpdate(BaseModel):
    """Request to update SSO configuration."""

    is_enabled: bool | None = None
    entity_id: str | None = None
    sso_url: str | None = None
    x509_cert: str | None = None
    auto_provision_users: bool | None = None
    jit_enabled: bool | None = None
    role_mapping: dict | None = None


@router.get("/providers", response_model=list[str])
async def list_sso_providers():
    """List available SSO providers."""
    return [p.value for p in SSOProvider]


@router.get("/config/{workspace_id}", response_model=SSOConfigResponse | None)
async def get_sso_config(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get SSO configuration for a workspace."""
    result = await db.execute(
        select(SSOConfig).where(SSOConfig.workspace_id == workspace_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        return None

    return SSOConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        provider=config.provider.value
        if hasattr(config.provider, "value")
        else config.provider,
        is_enabled=config.is_enabled,
        entity_id=config.entity_id,
        sso_url=config.sso_url,
        auto_provision_users=config.auto_provision_users,
        jit_enabled=config.jit_enabled,
        created_at=config.created_at,
    )


@router.post("/config", response_model=SSOConfigResponse)
async def create_sso_config(
    request: SSOConfigCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create SSO configuration for a workspace."""
    # Verify workspace access
    result = await db.execute(
        select(Workspace).where(Workspace.id == request.workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    try:
        provider = SSOProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {request.provider}",
        )

    config = SSOConfig(
        workspace_id=request.workspace_id,
        provider=provider,
        entity_id=request.entity_id,
        sso_url=request.sso_url,
        x509_cert=request.x509_cert,
        client_id=request.client_id,
        client_secret=request.client_secret,
        role_mapping=request.role_mapping,
        auto_provision_users=request.auto_provision_users,
        jit_enabled=request.jit_enabled,
    )
    db.add(config)
    await db.flush()
    await db.refresh(config)

    return SSOConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        provider=config.provider.value
        if hasattr(config.provider, "value")
        else config.provider,
        is_enabled=config.is_enabled,
        entity_id=config.entity_id,
        sso_url=config.sso_url,
        auto_provision_users=config.auto_provision_users,
        jit_enabled=config.jit_enabled,
        created_at=config.created_at,
    )


@router.patch("/config/{config_id}", response_model=SSOConfigResponse)
async def update_sso_config(
    config_id: str,
    request: SSOConfigUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update SSO configuration."""
    result = await db.execute(select(SSOConfig).where(SSOConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO config not found",
        )

    if request.is_enabled is not None:
        config.is_enabled = request.is_enabled
    if request.entity_id is not None:
        config.entity_id = request.entity_id
    if request.sso_url is not None:
        config.sso_url = request.sso_url
    if request.x509_cert is not None:
        config.x509_cert = request.x509_cert
    if request.auto_provision_users is not None:
        config.auto_provision_users = request.auto_provision_users
    if request.jit_enabled is not None:
        config.jit_enabled = request.jit_enabled
    if request.role_mapping is not None:
        config.role_mapping = request.role_mapping

    await db.flush()
    await db.refresh(config)

    return SSOConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        provider=config.provider.value
        if hasattr(config.provider, "value")
        else config.provider,
        is_enabled=config.is_enabled,
        entity_id=config.entity_id,
        sso_url=config.sso_url,
        auto_provision_users=config.auto_provision_users,
        jit_enabled=config.jit_enabled,
        created_at=config.created_at,
    )


@router.get("/login/{workspace_id}")
async def initiate_sso_login(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Initiate SSO login flow."""
    result = await db.execute(
        select(SSOConfig).where(
            SSOConfig.workspace_id == workspace_id,
            SSOConfig.is_enabled == True,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO not configured for this workspace",
        )

    # For SAML, redirect to IdP
    if config.provider in [SSOProvider.SAML, SSOProvider.OKTA, SSOProvider.AZURE_AD]:
        if not config.sso_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SSO URL not configured",
            )

        # Generate SAML AuthnRequest or redirect to IdP
        # This is a simplified redirect - real implementation would generate SAMLRequest
        state = uuid.uuid4().hex
        redirect_url = (
            f"{config.sso_url}?SAMLRequest=base64_encoded_request&RelayState={state}"
        )

        return RedirectResponse(url=redirect_url, status_code=302)

    # For OAuth-based SSO (Google Workspace)
    if config.provider == SSOProvider.GOOGLE:
        if not config.client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client ID not configured",
            )

        # Build OAuth redirect URL
        redirect_uri = f"/api/sso/callback/google"
        scopes = "openid email profile"
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={config.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&response_type=code"
            f"&state={workspace_id}"
        )

        return RedirectResponse(url=oauth_url, status_code=302)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Provider {config.provider} not fully implemented",
    )


@router.post("/saml/acs")
async def saml_acs(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """SAML Assertion Consumer Service - handles IdP response."""
    # In production, this would:
    # 1. Parse SAMLResponse from form data
    # 2. Validate signature using x509 cert
    # 3. Extract user attributes
    # 4. Create/update user if JIT enabled
    # 5. Create session

    form_data = await request.form()
    saml_response = form_data.get("SAMLResponse")

    if not saml_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing SAMLResponse",
        )

    # TODO: Implement SAML validation
    # For now, return placeholder response
    return {
        "message": "SAML ACS endpoint - needs production SAML library",
        "note": "Implement with python3-saml or similar",
    }


@router.get("/callback/google")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback."""
    # In production, this would:
    # 1. Exchange code for tokens
    # 2. Validate ID token
    # 3. Extract user info
    # 4. Create/update user
    # 5. Create session

    # TODO: Implement Google OAuth flow
    return {
        "message": "Google callback - needs production OAuth implementation",
        "workspace_id": state,
    }


@router.get("/metadata/{workspace_id}")
async def get_saml_metadata(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get SP metadata for SAML configuration."""
    result = await db.execute(
        select(SSOConfig).where(
            SSOConfig.workspace_id == workspace_id,
            SSOConfig.is_enabled == True,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO not configured for this workspace",
        )

    # Return basic SP metadata
    return {
        "entity_id": f"https://synthesis.app/saml/{workspace_id}",
        "acs_url": "https://synthesis.app/api/sso/saml/acs",
        "slo_url": "https://synthesis.app/api/sso/saml/slo",
    }


@router.delete("/config/{config_id}")
async def delete_sso_config(
    config_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete SSO configuration."""
    result = await db.execute(select(SSOConfig).where(SSOConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO config not found",
        )

    await db.delete(config)
    await db.flush()

    return {"message": "SSO configuration deleted"}
