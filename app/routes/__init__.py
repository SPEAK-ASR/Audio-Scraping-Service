"""
Routes package for the YouTube Audio Processing Pipeline.

This package contains all API route definitions organized by functionality.
"""

from .youtube import router as youtube_router
from .health import router as health_router
from .statistics import router as statistics_router
from .channels import router as channels_router
from .playlists import router as playlist_router

__all__ = ["youtube_router", "health_router", "statistics_router", "channels_router", "playlist_router"]