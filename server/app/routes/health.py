"""
Health check and system status routes.

This module contains routes for monitoring the health and status
of the YouTube Audio Processing Pipeline application.
"""

from fastapi import APIRouter

from app.core.config import settings

# Create router
router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Basic health status and application version
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME
    }


@router.get("/status")
async def system_status():
    """
    Detailed system status endpoint.
    
    Returns:
        More detailed system information including configuration status
    """
    return {
        "status": "operational",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "debug_mode": settings.DEBUG,
        "database_configured": bool(settings.DATABASE_URL),
        "cloud_storage_configured": bool(settings.GCS_BUCKET_NAME),
        "api_version": settings.API_V1_STR
    }