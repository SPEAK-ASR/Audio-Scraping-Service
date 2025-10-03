"""
Application configuration settings.

This module manages all configuration settings for the Sinhala ASR Dataset
Collection Service using Pydantic BaseSettings for type validation and
environment variable loading.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings with environment variable support and validation.
    
    All settings can be overridden via environment variables.
    Required variables: DATABASE_URL, GCS_BUCKET_NAME
    """
    
    # Application metadata
    APP_NAME: str = "YouTube Audio Processing Pipeline"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Google Cloud Storage configuration
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")
    SERVICE_ACCOUNT_B64: Optional[str] = os.getenv("SERVICE_ACCOUNT_B64")
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]

    class Config:
        """Pydantic configuration class."""
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()
