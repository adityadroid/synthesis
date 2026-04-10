"""Authentication service for user management and JWT tokens."""

from datetime import datetime, timedelta
from typing import Tuple
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..models.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from ..config import Settings


settings = Settings()

# JWT settings
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(user_id: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    """Decode and validate a JWT token, returning user_id if valid."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def signup(
    db: AsyncSession, request: SignupRequest
) -> Tuple[User | None, str | None]:
    """
    Register a new user.
    Returns (User, error_message)
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        return None, "Email already registered"

    # Create new user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        full_name=request.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user, None


async def login(
    db: AsyncSession, request: LoginRequest
) -> Tuple[User | None, str | None]:
    """
    Authenticate a user.
    Returns (User, error_message)
    """
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user:
        return None, "Invalid email or password"

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        return None, "Invalid email or password"

    if not user.is_active:
        return None, "Account is disabled"

    return user, None


async def refresh_access_token(refresh_token: str) -> Tuple[str | None, str | None]:
    """
    Refresh access token using refresh token.
    Returns (access_token, error_message)
    """
    user_id = decode_token(refresh_token)
    if not user_id:
        return None, "Invalid or expired refresh token"

    # Create new access token
    access_token = create_access_token(user_id)
    return access_token, None


def create_tokens(user_id: str) -> TokenResponse:
    """Create both access and refresh tokens."""
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
