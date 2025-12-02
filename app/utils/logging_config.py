"""
Logging configuration for the YouTube Audio Processing Pipeline.

Provides centralized logging setup with proper formatting, levels,
and output configuration for development and production environments.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure application logging with appropriate formatting and handlers.
    
    Args:
        level: Optional logging level override. If not provided, uses DEBUG 
               mode from settings to determine level.
    """
    # Determine logging level
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to appropriate levels
    _configure_third_party_loggers()
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")


def _configure_third_party_loggers() -> None:
    """Configure third-party library loggers to reduce noise."""
    # Reduce Google Cloud library verbosity
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("google.cloud").setLevel(logging.WARNING)
    
    # Reduce SQLAlchemy verbosity (unless in debug mode)
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Reduce uvicorn access log verbosity
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Reduce yt-dlp verbosity but keep errors visible
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    
    # Keep fastapi logs at info level
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name, typically __name__ from the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)