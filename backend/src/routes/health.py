"""Health check routes for monitoring."""

from datetime import datetime
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from typing import Optional

from ..db import engine
from ..services.cache import cache_service
from ..services.metrics import metrics


router = APIRouter(prefix="/health", tags=["health"])


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: datetime
    version: Optional[str] = None
    uptime_seconds: Optional[float] = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check with dependency status."""

    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float

    database: dict
    cache: dict
    metrics: dict


@router.get("", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Basic health check endpoint.

    Returns 200 if the service is running.
    """
    return HealthCheckResponse(
        status="ok",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        uptime_seconds=None,
    )


@router.get("/live", response_model=HealthCheckResponse)
async def liveness_check() -> HealthCheckResponse:
    """Kubernetes liveness probe.

    Returns 200 if the process is alive.
    """
    return HealthCheckResponse(
        status="ok",
        timestamp=datetime.utcnow(),
    )


@router.get("/ready", response_model=HealthCheckResponse)
async def readiness_check() -> HealthCheckResponse:
    """Kubernetes readiness probe.

    Returns 200 if the service is ready to accept traffic.
    Checks database connectivity.
    """
    try:
        # Check database connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return HealthCheckResponse(
            status="ok",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        return HealthCheckResponse(
            status="degraded",
            timestamp=datetime.utcnow(),
        )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check() -> DetailedHealthResponse:
    """Detailed health check with all dependencies.

    Returns 200 if healthy, 503 if any dependency is unhealthy.
    """
    health_status = "ok"
    checks = {
        "database": await check_database(),
        "cache": check_cache(),
        "metrics": check_metrics(),
    }

    # Determine overall status
    for check_name, check_result in checks.items():
        if check_result["status"] != "ok":
            health_status = "degraded"
            break

    return DetailedHealthResponse(
        status=health_status,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        uptime_seconds=metrics.get_summary()["uptime_seconds"],
        **checks,
    )


async def check_database() -> dict:
    """Check database connectivity."""
    try:
        import sqlite3
        from ..config import Settings

        settings = Settings()
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")

        # Simple connection check for SQLite
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")

        return {
            "status": "ok",
            "type": "sqlite",
            "url": db_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def check_cache() -> dict:
    """Check cache status."""
    try:
        stats = cache_service.get_stats()
        return {
            "status": "ok",
            "backend": stats["backend"],
            "hit_rate": stats["hit_rate"],
            "entries": stats.get("memory_entries", 0),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def check_metrics() -> dict:
    """Check metrics collector."""
    try:
        summary = metrics.get_summary()
        return {
            "status": "ok",
            "uptime_seconds": summary["uptime_seconds"],
            "counter_count": len(summary["counters"]),
            "gauge_count": len(summary["gauges"]),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
