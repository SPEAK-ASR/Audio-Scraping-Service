"""
Health check and system status routes.

This module contains routes for monitoring the health and status
of the YouTube Audio Processing Pipeline application.
"""

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.database import health_check

# Create router
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check_endpoint():
    """
    Health check endpoint with database connectivity check.
    
    Returns:
        Basic health status, application version, and database status
    """
    db_healthy = await health_check()
    
    if not db_healthy:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "database": "connected"
    }


@router.get("/status")
async def system_status():
    """
    Detailed system status endpoint with database health check.
    
    Returns:
        More detailed system information including configuration and database status
    """
    db_healthy = await health_check()
    
    return {
        "status": "operational" if db_healthy else "degraded",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "debug_mode": settings.DEBUG,
        "database_configured": bool(settings.DATABASE_URL),
        "database_healthy": db_healthy,
        "cloud_storage_configured": bool(settings.GCS_BUCKET_NAME),
        "api_version": settings.API_V1_STR
    }