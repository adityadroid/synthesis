"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings

settings = Settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "message": "Synthesis backend is running"}


@app.get("/api/health")
async def api_health_check() -> dict:
    """API health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
