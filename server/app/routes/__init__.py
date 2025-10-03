"""
Routes package for the YouTube Audio Processing Pipeline.

This package contains all API route definitions organized by functionality.
"""

from .youtube import router as youtube_router
from .health import router as health_router

__all__ = ["youtube_router", "health_router"]