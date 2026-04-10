"""API key routes for programmatic access."""

import json
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..db import get_db
from ..models.api_key import APIKey, APIKeyScope, DEFAULT_SCOPES
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class APIKeyResponse(BaseModel):
    """API key response (without the actual key)."""

    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    is_active: bool
    last_used_at: datetime | None
    request_count: int
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateAPIKeyRequest(BaseModel):
    """Request to create an API key."""

    name: str
    scopes: list[str] | None = None
    expires_in_days: int | None = None  # None = no expiration


class APIKeyCreatedResponse(BaseModel):
    """Response when key is created (includes the actual key)."""

    id: str
    name: str
    key: str  # The actual key - only shown once!
    key_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime


@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all API keys for the current user."""
    result = await db.execute(
        select(APIKey)
        .where(APIKey.user_id == user_id)
        .order_by(desc(APIKey.created_at))
    )
    keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            scopes=k.get_scopes(),
            is_active=k.is_active,
            last_used_at=k.last_used_at,
            request_count=k.request_count,
            expires_at=k.expires_at,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.post("", response_model=APIKeyCreatedResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key. The key is only shown once!"""
    # Generate the key
    raw_key, key_hash, key_prefix = APIKey.generate_key()

    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

    # Get scopes
    scopes = request.scopes if request.scopes else [s.value for s in DEFAULT_SCOPES]

    # Validate scopes
    valid_scopes = [s.value for s in APIKeyScope]
    for scope in scopes:
        if scope not in valid_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scope: {scope}",
            )

    # Create the key record
    api_key = APIKey(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=request.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=json.dumps(scopes),
        expires_at=expires_at,
    )
    db.add(api_key)
    await db.flush()

    return APIKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key=raw_key,  # Only shown once!
        key_prefix=api_key.key_prefix,
        scopes=scopes,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == user_id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        scopes=api_key.get_scopes(),
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        request_count=api_key.request_count,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


@router.post("/{key_id}/deactivate")
async def deactivate_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate an API key (can be reactivated)."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == user_id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False
    await db.flush()

    return {"message": "API key deactivated", "id": api_key.id}


@router.post("/{key_id}/activate")
async def activate_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reactivate a deactivated API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == user_id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    if api_key.is_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate expired key",
        )

    api_key.is_active = True
    await db.flush()

    return {"message": "API key activated", "id": api_key.id}


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete an API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == user_id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.flush()

    return {"message": "API key deleted"}


@router.get("/scopes/list", response_model=list[str])
async def list_scopes():
    """List all available API key scopes."""
    return [scope.value for scope in APIKeyScope]


# Need to import BaseModel at top, using Pydantic v2 style
from pydantic import BaseModel

APIKeyResponse.model_rebuild()
APIKeyCreatedResponse.model_rebuild()
