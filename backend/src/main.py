"""FastAPI application entry point."""

import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import Settings
from .db import init_db
from .routes import (
    auth,
    users,
    chat,
    models,
    export,
    usage,
    upload,
    templates,
    workspaces,
    tools,
    admin,
    api_keys,
    sso,
    health,
    metrics,
)

# Services
from .services.logging import setup_logging, get_logger, request_id_var
from .services.cache import cache_service
from .services.metrics import metrics as metrics_collector
from .middleware.rate_limit import RateLimitMiddleware, RateLimitConfig
from .middleware.request_id import RequestIDMiddleware

settings = Settings()

# Initialize logging
setup_logging(debug=settings.debug)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and services on startup."""
    logger.info("Starting Synthesis backend", version="0.1.0")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize cache
    await cache_service.initialize()
    logger.info("Cache initialized")

    yield

    # Cleanup
    logger.info("Shutting down Synthesis backend")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware in order
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    config=RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_size=10,
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    request_id = request_id_var.get() or "unknown"
    logger.exception(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "request_id": request_id,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": str(exc),
        },
    )


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(usage.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(workspaces.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(api_keys.router, prefix="/api")
app.include_router(sso.router, prefix="/api")

# Health and metrics endpoints
app.include_router(health.router)
app.include_router(metrics.router)


# Basic health check
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Synthesis backend is running",
        "version": "0.1.0",
    }


@app.get("/api/health")
async def api_health_check() -> dict:
    """API health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "uptime": time.time(),
    }
