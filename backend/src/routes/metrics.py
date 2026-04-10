"""Prometheus metrics endpoint."""

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from ..services.metrics import metrics


router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics() -> PlainTextResponse:
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    output = metrics.get_prometheus_output()
    return PlainTextResponse(
        content=output,
        media_type="text/plain; charset=utf-8",
    )


@router.get("/metrics/summary")
async def metrics_summary():
    """Get metrics as JSON for debugging."""
    return metrics.get_summary()
