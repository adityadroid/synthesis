"""User routes for profile and session management."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models.auth import UserResponse
from ..models import User
from ..services import auth as auth_service
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


# Request/Response schemas
class UpdateProfileRequest(BaseModel):
    """Update profile request schema."""

    full_name: str | None = None


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""

    current_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    """Delete account request schema."""

    password: str


class MessageResponse(BaseModel):
    """Message response schema."""

    message: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information."""
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile (full_name, etc)."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if request.full_name is not None:
        user.full_name = request.full_name
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify current password
    if not auth_service.verify_password(request.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    user.hashed_password = auth_service.get_password_hash(request.new_password)
    await db.commit()
    return MessageResponse(message="Password changed successfully")


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    request: DeleteAccountRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete user account and all data."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify password
    if not auth_service.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )

    # Delete user (cascade will delete conversations and messages)
    await db.delete(user)
    await db.commit()
    return MessageResponse(message="Account deleted successfully")
