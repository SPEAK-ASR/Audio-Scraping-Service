"""
Monitoring and diagnostics routes.

This module provides endpoints for monitoring database connection pool status,
active connections, and system health specifically for debugging connection issues.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload
from typing import Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
import json
import os
from pathlib import Path

from app.core.database import async_engine, AsyncSessionLocal
from app.models.audio import Audio
from app.models.youtube_video import YouTubeVideo
from app.services.cloud_storage import CloudStorageService
from app.schemas.audio_schemas import AudioDurationMismatchResponse, VideoMismatchInfo, MismatchedAudio
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

        # Current pool statistics
        current_pool_size = pool.size()
        checked_out = pool.checkedout()
        overflow = pool.overflow()
        total_connections = current_pool_size + overflow

        # Configured limits from the pool's public attributes, if available
        configured_pool_size = getattr(pool, "pool_size", None)
        configured_max_overflow = getattr(pool, "max_overflow", None)
        max_possible_connections = (
            configured_pool_size + configured_max_overflow
            if configured_pool_size is not None and configured_max_overflow is not None
            else None
        )

        # Derive a status based on utilization if we know the configured maximum
        if max_possible_connections and max_possible_connections > 0:
            usage_ratio = checked_out / max_possible_connections
            if usage_ratio < 0.75:
                status = "healthy"
            elif usage_ratio < 0.9:
                status = "warning"
            else:
                status = "critical"
        else:
            status = "unknown"

        # Assemble pool status payload
        pool_status = {
            "pool_size": current_pool_size,
            "checked_out": checked_out,
            "overflow": overflow,
            "total_connections": total_connections,
            "configured_pool_size": configured_pool_size,
            "configured_max_overflow": configured_max_overflow,
            "max_possible_connections": max_possible_connections,
            "status": status,
        }

        logger.info(
            "Pool status check: %s/%s connections in use",
            checked_out,
            max_possible_connections if max_possible_connections is not None else "unknown",
        )
        return pool_status
        
    except Exception as e:
        logger.error(f"Failed to get pool status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pool status: {str(e)}")


@router.get("/pool-diagnostics")
async def get_pool_diagnostics() -> Dict[str, Any]:
    """
    Get detailed pool diagnostics for troubleshooting connection issues.
    
    Returns comprehensive pool metrics including:
    - Pool configuration
    - Current usage statistics
    - Connection lifecycle metrics
    - Health status and recommendations
    """
    try:
        pool = async_engine.pool
        
        # Get basic pool metrics
        pool_status = {
            "size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "configured_pool_size": getattr(pool, "pool_size", None),
            "configured_max_overflow": getattr(pool, "max_overflow", None),
            "pool_timeout": getattr(pool, "timeout", None),
        }
        
        # Calculate utilization
        max_connections = pool_status["configured_pool_size"] + pool_status["configured_max_overflow"]
        utilization = (pool_status["checked_out"] / max_connections * 100) if max_connections else 0
        
        # Determine health status
        if utilization < 60:
            health = "healthy"
            recommendation = "Pool is operating normally"
        elif utilization < 80:
            health = "warning"
            recommendation = "Pool utilization is high - monitor for potential issues"
        elif utilization < 95:
            health = "critical"
            recommendation = "Pool near exhaustion - investigate connection leaks or increase pool size"
        else:
            health = "exhausted"
            recommendation = "Pool exhausted - immediate action required"
        
        return {
            "pool_status": pool_status,
            "utilization_percent": round(utilization, 2),
            "health": health,
            "recommendation": recommendation,
            "max_connections": max_connections
        }
        
    except Exception as e:
        logger.error(f"Failed to get pool diagnostics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pool diagnostics: {str(e)}")


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


@router.get("/audio-duration-mismatch")
async def check_audio_duration_mismatch(
    min_date: Optional[str] = Query(
        None,
        description="Minimum date (YYYY-MM-DD) to filter videos by created_at. Only checks audios from videos created after this date."
    )
):
    """
    Check for mismatches between database padded_duration and actual cloud storage audio duration.
    
    Compares the padded_duration stored in the database with the actual duration 
    of audio files in the cloud bucket. Returns all mismatched audios grouped by video.
    
    Args:
        min_date: Optional minimum date filter (YYYY-MM-DD format)
    
    Returns:
        AudioDurationMismatchResponse with total mismatch count and detailed video information
    """
    try:
        logger.info(f"Starting audio duration mismatch check (min_date: {min_date})")
        
        # Parse min_date if provided
        min_datetime = None
        if min_date:
            try:
                min_datetime = datetime.strptime(min_date, "%Y-%m-%d")
                logger.info(f"Filtering audios from videos created after {min_datetime}")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD format."
                )
        
        # Fetch audio data from database first, then close connection
        async with AsyncSessionLocal() as session:
            # Build query
            query = (
                select(Audio)
                .join(Audio.youtube_video)
                .options(selectinload(Audio.youtube_video))
                .where(Audio.padded_duration.isnot(None))
            )
            
            # Apply date filter if provided
            if min_datetime:
                query = query.where(YouTubeVideo.created_at >= min_datetime)
            
            result = await session.execute(query)
            audios = result.scalars().all()
            
            logger.info(f"Found {len(audios)} audios with padded_duration to check")
            
            if not audios:
                # Create empty response and return file
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"audio_duration_mismatch_{timestamp}.json"
                filepath = data_dir / filename
                
                empty_response = {
                    "total_mismatch_audios": 0,
                    "total_relevant_videos": 0,
                    "videos": []
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(empty_response, f, indent=2)
                
                return FileResponse(
                    path=str(filepath),
                    media_type="application/json",
                    filename=filename
                )
            
            # Extract data we need before closing the session
            audio_data = [
                {
                    "audio_filename": audio.audio_filename,
                    "padded_duration": audio.padded_duration,
                    "video_id": audio.youtube_video.video_id if audio.youtube_video else "unknown"
                }
                for audio in audios
            ]
        
        # Database session is now closed, safe to do long-running operations
        
        # Initialize cloud storage service
        cloud_storage = CloudStorageService()
        
        # Get all audio filenames for batch processing
        audio_filenames = [item["audio_filename"] for item in audio_data]
        
        # Batch download and get durations with progress bar
        logger.info("Fetching audio durations from cloud storage (this may take a while)...")
        print(f"\n🔍 Checking {len(audio_data)} audio files for duration mismatches...")
        
        # Use tqdm progress bar
        durations_dict = {}
        batch_size = 30  # Process in smaller batches to avoid connection pool issues
        
        with tqdm(total=len(audio_filenames), desc="Checking audio durations", unit="file") as pbar:
            for i in range(0, len(audio_filenames), batch_size):
                batch = audio_filenames[i:i + batch_size]
                batch_durations = await cloud_storage.get_audio_durations_batch(batch, max_concurrent=8)
                durations_dict.update(batch_durations)
                pbar.update(len(batch))
        
        # Group audios by video and compare durations
        video_groups = defaultdict(lambda: {"correct": [], "mismatch": []})
        total_mismatch_count = 0
        tolerance = 0.1  # 0.1 second tolerance for rounding
        
        logger.info("Analyzing duration differences...")
        print("\n📊 Analyzing duration differences...")
        
        for item in tqdm(audio_data, desc="Analyzing", unit="audio"):
            actual_duration = durations_dict.get(item["audio_filename"])
            
            # Skip if we couldn't get the actual duration
            if actual_duration is None:
                continue
            
            # Compare durations
            duration_diff = abs(item["padded_duration"] - actual_duration)
            video_id = item["video_id"]
            
            if duration_diff > tolerance:
                # Mismatch found
                video_groups[video_id]["mismatch"].append({
                    "audio_filename": item["audio_filename"],
                    "database_duration": item["padded_duration"],
                    "actual_duration": actual_duration
                })
                total_mismatch_count += 1
            else:
                # Duration matches
                video_groups[video_id]["correct"].append(item["audio_filename"])
        
        # Build response - use plain dicts instead of Pydantic models
        videos_list = []
        for video_id, audios_info in video_groups.items():
            if audios_info["mismatch"]:  # Only include videos with mismatches
                videos_list.append({
                    "video_id": video_id,
                    "correct_audio_count": len(audios_info["correct"]),
                    "mismatch_audio_count": len(audios_info["mismatch"]),
                    "mismatched_audios": audios_info["mismatch"]
                })
        
        result_msg = (
            f"\n✅ Mismatch check complete: {total_mismatch_count} mismatches "
            f"across {len(videos_list)} videos"
        )
        logger.info(result_msg)
        print(result_msg)
        
        # Create data directory if it doesn't exist
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Create response data
        response_data = {
            "total_mismatch_audios": total_mismatch_count,
            "total_relevant_videos": len(videos_list),
            "videos": videos_list
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_duration_mismatch_{timestamp}.json"
        filepath = data_dir / filename
        
        # Write to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Response written to {filepath}")
        print(f"\n💾 Response saved to: {filepath}")
        
        # Return file as download
        return FileResponse(
            path=str(filepath),
            media_type="application/json",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check audio duration mismatch: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to check audio duration mismatch: {str(e)}"
        )
