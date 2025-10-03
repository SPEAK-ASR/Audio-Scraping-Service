"""
FastAPI application for YouTube audio processing and transcription pipeline.

This is the main application entry point that handles app initialization,
middleware setup, and route registration.
"""

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.gcp_auth import gcp_auth_manager
from app.routes import youtube_router, health_router
from app.utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown logic including database initialization
    and GCP authentication setup.
    """
    # Startup
    logger.info("Starting application...")
    
    # Initialize database connection
    await init_database()
    logger.info("Database initialized")
    
    # Setup GCP authentication
    gcp_auth_manager.setup_credentials()
    logger.info("GCP authentication configured")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close database connection
    await close_database()
    logger.info("Database connection closed")
    
    # Cleanup GCP resources
    gcp_auth_manager.cleanup()
    logger.info("GCP resources cleaned up")
    
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Create FastAPI app with lifespan
    app = FastAPI(
        title=settings.APP_NAME,
        description="API for processing YouTube videos into audio clips with optional transcription",
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health_router)
    app.include_router(youtube_router)
    
    # Mount static files for audio clips
    app.mount("/output", StaticFiles(directory="output"), name="audio_files")

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )