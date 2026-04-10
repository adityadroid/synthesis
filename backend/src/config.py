"""Backend configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App settings
    app_name: str = "Synthesis"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # Database - using SQLite for local development
    database_url: str = "sqlite+aiosqlite:///./synthesis.db"

    # Redis cache (optional)
    redis_url: str = ""

    # LLM API Keys (optional - can be set later)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Sentry error tracking (optional)
    sentry_dsn: str = ""

    # OpenTelemetry (optional)
    otel_exporter: str = ""
    otel_service_name: str = "synthesis-backend"

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000

    # Content moderation
    moderation_level: str = "medium"  # none, low, medium, high

    model_config = {"env_file": ".env", "extra": "ignore"}
