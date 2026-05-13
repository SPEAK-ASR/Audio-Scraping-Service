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
# Pool sized for concurrent video processing with transcription workloads
# Transcription of 287 clips in batches of 5 = ~60 concurrent operations
# Each operation may need 1-2 connections
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=30,         # Increased base pool for heavy concurrent transcription
    max_overflow=30,      # Burst capacity (total 60 connections)
    pool_timeout=120,     # Increased timeout to 120s for heavy concurrent load
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections every hour
    connect_args={
        "timeout": 120,             # Connection timeout (asyncpg parameter)
        "command_timeout": 120,     # Command timeout in seconds (increased for heavy load)
        "server_settings": {
            "application_name": "audio_scraping_service",
            "statement_timeout": "30000",  # 30 second timeout for queries (in milliseconds)
            "idle_in_transaction_session_timeout": "60000"  # 60 sec idle in transaction timeout
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
    
    IMPORTANT: This dependency automatically commits on success and rolls back on error.
    Endpoints using this should not manually commit unless they need fine-grained control.
    """
    session = None
    try:
        session = AsyncSessionLocal()        
        # Log pool status for monitoring (only in debug mode to avoid overhead)
        if settings.DEBUG:
            pool = async_engine.pool
            logger.debug(f"DB Session acquired - Pool status: {pool.checkedout()}/{pool.size() + pool.overflow()} connections in use")
                # Test the connection before yielding
        await session.execute(text("SELECT 1"))
        yield session
        
        # Auto-commit if transaction is still active and no exception occurred
        if session.in_transaction():
            await session.commit()
            
    except Exception as e:
        # Don't log HTTPExceptions as database errors - they're application logic
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            # HTTPException should propagate normally, just clean up the session
            if session:
                try:
                    if session.in_transaction():
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
                    if session.in_transaction():
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
    
    Uses a lightweight session from the pool with a short timeout to avoid
    exhausting the pool during heavy operations. If pool is exhausted,
    returns False instead of blocking.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    session = None
    try:
        # Use a session with a very short timeout for health checks
        # This prevents health checks from blocking during heavy load
        session = AsyncSessionLocal()
        result = await asyncio.wait_for(
            session.execute(text("SELECT 1")),
            timeout=5.0  # 5 second timeout for health checks
        )
        return True
    except asyncio.TimeoutError:
        logger.warning("Database health check timed out (pool may be under heavy load)")
        return False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
    finally:
        if session:
            await _safe_session_close(session)
