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
    SUPABASE_SERVICE_ROLE_KEY: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Google Cloud Storage configuration
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")
    SERVICE_ACCOUNT_B64: Optional[str] = os.getenv("SERVICE_ACCOUNT_B64")
    
    # Audio processing configuration
    MIN_CLIP_DURATION: float = 4.0  # Minimum clip duration in seconds
    MAX_CLIP_DURATION: float = 10.0  # Maximum clip duration in seconds
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]  # Deprecated, use ALLOWED_ORIGINS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    @property
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list of origins."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        """Pydantic configuration class."""
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()
