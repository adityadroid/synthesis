"""Pydantic models for authentication."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request schema."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    full_name: str | None
    created_at: str

    model_config = {"from_attributes": True}
