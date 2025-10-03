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


@router.post("/init-db")
async def initialize_database():
    """
    Initialize database tables (development only).
    
    This endpoint creates database tables if they don't exist.
    Only available in debug mode for development purposes.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="Database initialization is only available in debug mode"
        )
    
    try:
        from app.core.database import async_engine, Base
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        return {
            "success": True,
            "message": "Database tables initialized successfully",
            "debug_mode": settings.DEBUG
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize database: {str(e)}"
        )