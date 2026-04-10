"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .db import init_db
from .routes import auth, users, chat, models, export, usage, upload, templates


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(usage.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(templates.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "message": "Synthesis backend is running"}


@app.get("/api/health")
async def api_health_check() -> dict:
    """API health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
