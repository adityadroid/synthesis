"""Backend configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "AI Chat"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Database - using SQLite for local development
    database_url: str = "sqlite+aiosqlite:///./aichat.db"

    # LLM API Keys (optional - can be set later)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}
