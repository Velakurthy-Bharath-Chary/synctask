"""Application and database health checks used by the FastAPI app."""

import logging

from app.database import check_db_connection

logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """Log application startup for callers that use explicit event hooks."""
    logger.info("TaskSyncer application startup")


async def shutdown_event() -> None:
    """Log application shutdown for callers that use explicit event hooks."""
    logger.info("TaskSyncer application shutdown")


async def health_check() -> dict:
    """Return the API and database health state."""
    database_healthy = await check_db_connection()
    return {
        "status": "healthy" if database_healthy else "unhealthy",
        "database": "connected" if database_healthy else "disconnected",
    }
