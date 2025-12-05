"""
Database configuration and connection management.

This module provides asynchronous database connectivity using SQLAlchemy
with asyncpg driver for PostgreSQL. It includes connection lifecycle
management and session factory for dependency injection.
"""

from typing import AsyncGenerator
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DBAPIError, DisconnectionError

from app.core.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    
    This declarative base provides the foundation for all database models
    in the application with automatic table mapping and relationship support.
    """
    pass


# Convert standard PostgreSQL URL to asyncpg format
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Create async database engine with connection pooling
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    connect_args={
        "command_timeout": 60,      # Command timeout in seconds
        "server_settings": {
            "application_name": "audio_scraping_service"
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous SQLAlchemy `AsyncSession`.
    
    Handles connection failures gracefully during session cleanup to prevent
    cascading errors when database connections are lost.
    """
    session = None
    try:
        session = AsyncSessionLocal()
        # Test the connection before yielding
        await session.execute(text("SELECT 1"))
        yield session
    except Exception as e:
        # Don't log HTTPExceptions as database errors - they're application logic
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            # HTTPException should propagate normally, just clean up the session
            if session:
                try:
                    await session.rollback()
                except (DBAPIError, DisconnectionError):
                    # Connection issues during rollback are expected and OK
                    pass
                except Exception as rollback_error:
                    logger.warning(f"Error during session rollback for HTTPException: {rollback_error}")
            raise
        else:
            # This is a real database/connection error
            logger.error(f"Async database session error: {e}", exc_info=True)
            if session:
                try:
                    await session.rollback()
                except (DBAPIError, DisconnectionError) as rollback_error:
                    # Connection was lost during rollback - this is expected in some scenarios
                    logger.warning(f"Failed to rollback transaction due to connection loss: {rollback_error}")
                except Exception as rollback_error:
                    logger.error(f"Unexpected error during session rollback: {rollback_error}")
            raise
    finally:
        if session:
            await _safe_session_close(session)


async def _safe_session_close(session: AsyncSession) -> None:
    """
    Safely close an async session with proper exception handling.
    
    This function handles various connection-related errors that can occur
    during session cleanup, preventing them from propagating up and causing
    application crashes.
    """
    try:
        await session.close()
    except (DBAPIError, DisconnectionError) as e:
        # Connection was already lost - this is not an error we need to propagate
        logger.warning(f"Session close failed due to connection loss (expected): {e}")
    except Exception as e:
        # Log unexpected errors but don't raise them to prevent cascading failures
        logger.error(f"Unexpected error during session close: {e}")
    finally:
        # Ensure session is marked as closed even if close() failed
        try:
            if hasattr(session, '_connection') and session._connection:
                # Force close the underlying connection if it still exists
                await session._connection.close()
        except Exception as e:
            logger.debug(f"Could not force close connection: {e}")

async def init_database() -> None:
    """Initialize database connection (async) and verify connectivity."""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Async database connection established successfully")
                return
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to initialize async database after {max_retries} attempts: {e}")
                raise
            else:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)


async def close_database() -> None:
    """Dispose the async engine with proper error handling."""
    try:
        await async_engine.dispose()
        logger.info("Async database connection closed")
    except Exception as e:
        logger.error(f"Error closing async database connection: {e}")
        # Don't re-raise here to allow graceful shutdown


async def health_check() -> bool:
    """
    Perform a database health check.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
