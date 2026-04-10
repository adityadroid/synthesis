"""Database connection and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .config import Settings
from .models import Base


settings = Settings()
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables and run migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Run migrations to add missing columns
        await _run_migrations(conn)


async def _run_migrations(conn) -> None:
    """Add missing columns to existing tables."""
    from sqlalchemy import text

    # Get existing columns for messages table
    result = await conn.execute(text("PRAGMA table_info(messages)"))
    columns = [row[1] for row in result.fetchall()]

    # Add 'model' column if it doesn't exist (Phase 1 feature)
    if "model" not in columns:
        await conn.execute(text("ALTER TABLE messages ADD COLUMN model VARCHAR(50)"))
