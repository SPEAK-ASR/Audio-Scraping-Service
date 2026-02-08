"""
Monitoring and diagnostics routes.

This module provides endpoints for monitoring database connection pool status,
active connections, and system health specifically for debugging connection issues.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from typing import Dict, Any

from app.core.database import async_engine, AsyncSessionLocal
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


@router.get("/pool-status")
async def get_pool_status() -> Dict[str, Any]:
    """
    Get current connection pool status.
    
    Returns information about:
    - Current pool size (connections in use)
    - Checked out connections
    - Overflow connections (beyond pool_size)
    - Total possible connections (pool_size + max_overflow)
    
    This helps diagnose connection pool exhaustion issues.
    """
    try:
        pool = async_engine.pool
        
        # Get pool statistics
        pool_status = {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
            "configured_pool_size": async_engine.pool._pool.maxsize if hasattr(async_engine.pool, '_pool') else 15,
            "configured_max_overflow": async_engine.pool._max_overflow if hasattr(async_engine.pool, '_max_overflow') else 25,
            "max_possible_connections": 40,  # pool_size (15) + max_overflow (25)
            "status": "healthy" if pool.checkedout() < 30 else "warning" if pool.checkedout() < 35 else "critical"
        }
        
        logger.info(f"Pool status check: {pool_status['checked_out']}/{pool_status['max_possible_connections']} connections in use")
        
        return pool_status
        
    except Exception as e:
        logger.error(f"Failed to get pool status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pool status: {str(e)}")


@router.get("/active-connections")
async def get_active_connections() -> Dict[str, Any]:
    """
    Get database-level active connection statistics.
    
    Returns:
    - Total connections to the database
    - Active connections (currently executing queries)
    - Idle in transaction connections (stuck transactions - these are problematic!)
    - Idle connections
    
    High "idle_in_transaction" count indicates connection leaks.
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT 
                    count(*) as total,
                    count(*) FILTER (WHERE state = 'active') as active,
                    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                    count(*) FILTER (WHERE state = 'idle') as idle
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """))
            row = result.fetchone()
            
            connection_stats = {
                "total_connections": row[0],
                "active": row[1],
                "idle_in_transaction": row[2],
                "idle": row[3],
                "status": "healthy" if row[2] == 0 else "warning" if row[2] < 3 else "critical",
                "warning": "High idle_in_transaction count detected!" if row[2] > 2 else None
            }
            
            logger.info(f"Connection stats: {connection_stats['total_connections']} total, {connection_stats['idle_in_transaction']} idle in transaction")
            
            return connection_stats
            
    except Exception as e:
        logger.error(f"Failed to get active connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active connections: {str(e)}")


@router.get("/stuck-connections")
async def get_stuck_connections() -> Dict[str, Any]:
    """
    Get list of connections that are stuck in 'idle in transaction' state.
    
    These connections have started a transaction but haven't committed or rolled back.
    They hold onto database resources and prevent other operations from proceeding.
    
    Returns details about each stuck connection including:
    - Process ID (pid)
    - How long it's been stuck
    - The application name
    - The last query executed
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT 
                    pid,
                    usename,
                    application_name,
                    state,
                    query_start,
                    state_change,
                    EXTRACT(EPOCH FROM (NOW() - state_change)) as seconds_stuck,
                    query
                FROM pg_stat_activity 
                WHERE datname = current_database()
                  AND state = 'idle in transaction'
                ORDER BY state_change ASC
            """))
            
            stuck_connections = []
            for row in result:
                stuck_connections.append({
                    "pid": row[0],
                    "username": row[1],
                    "application": row[2],
                    "state": row[3],
                    "query_start": str(row[4]) if row[4] else None,
                    "state_change": str(row[5]) if row[5] else None,
                    "seconds_stuck": int(row[6]) if row[6] else 0,
                    "last_query": row[7][:200] if row[7] else None  # Truncate long queries
                })
            
            return {
                "count": len(stuck_connections),
                "connections": stuck_connections,
                "status": "healthy" if len(stuck_connections) == 0 else "warning" if len(stuck_connections) < 3 else "critical",
                "recommendation": "Consider killing stuck connections if they've been stuck for > 5 minutes" if len(stuck_connections) > 0 else None
            }
            
    except Exception as e:
        logger.error(f"Failed to get stuck connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stuck connections: {str(e)}")


@router.get("/database-config")
async def get_database_config() -> Dict[str, Any]:
    """
    Get key database configuration settings.
    
    Returns PostgreSQL configuration for:
    - max_connections
    - idle_in_transaction_session_timeout
    - statement_timeout
    
    Useful for understanding database-level limits.
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT name, setting, unit 
                FROM pg_settings 
                WHERE name IN (
                    'max_connections',
                    'idle_in_transaction_session_timeout',
                    'statement_timeout'
                )
            """))
            
            config = {}
            for row in result:
                config[row[0]] = {
                    "value": row[1],
                    "unit": row[2] if row[2] else "N/A"
                }
            
            return {
                "database_config": config,
                "application_pool_config": {
                    "pool_size": 15,
                    "max_overflow": 25,
                    "total_possible": 40
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to get database config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database config: {str(e)}")


@router.get("/summary")
async def get_monitoring_summary() -> Dict[str, Any]:
    """
    Get a comprehensive summary of all monitoring metrics.
    
    This endpoint combines pool status, connection stats, and stuck connection info
    into a single response for quick health assessment.
    """
    try:
        # Get all metrics
        pool_status = await get_pool_status()
        connection_stats = await get_active_connections()
        stuck_info = await get_stuck_connections()
        
        # Determine overall status
        statuses = [pool_status["status"], connection_stats["status"], stuck_info["status"]]
        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": str(__import__('datetime').datetime.now()),
            "pool": {
                "in_use": pool_status["checked_out"],
                "total_possible": pool_status["max_possible_connections"],
                "utilization_percent": round((pool_status["checked_out"] / pool_status["max_possible_connections"]) * 100, 1)
            },
            "database": {
                "total_connections": connection_stats["total_connections"],
                "active": connection_stats["active"],
                "stuck": connection_stats["idle_in_transaction"]
            },
            "issues": {
                "stuck_connections": stuck_info["count"],
                "pool_near_limit": pool_status["checked_out"] > 30,
                "warnings": [w for w in [connection_stats.get("warning"), stuck_info.get("recommendation")] if w]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring summary: {str(e)}")
