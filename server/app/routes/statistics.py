"""
Statistics routes for database analytics and metrics.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_database_session
from app.services.statistics_service import StatisticsService
from app.schemas.statistics_schemas import StatisticsResponse
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/statistics", tags=["Statistics"])


@router.get("", response_model=StatisticsResponse)
async def get_statistics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days for daily statistics"),
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get comprehensive database statistics including:
    - Total data summary
    - Duration by category/domain
    - Transcription status (transcribed vs non-transcribed)
    - Daily transcription trends
    - Admin contributions
    
    Args:
        days: Number of days to include in daily statistics (default: 30, max: 365)
        db: Database session
        
    Returns:
        Complete statistics data
    """
    try:
        logger.info(f"Fetching statistics for last {days} days")
        
        statistics = await StatisticsService.get_all_statistics(db, days)
        
        logger.info("Successfully retrieved statistics")
        return statistics
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get quick summary statistics only.
    
    Returns:
        Summary statistics including total videos, clips, and durations
    """
    try:
        logger.info("Fetching summary statistics")
        
        summary = await StatisticsService.get_total_summary(db)
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error fetching summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve summary: {str(e)}"
        )


@router.get("/categories")
async def get_category_durations(
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get duration statistics by category/domain.
    
    Returns:
        List of categories with their durations and clip counts
    """
    try:
        logger.info("Fetching category durations")
        
        categories = await StatisticsService.get_category_durations(db)
        
        return {
            "success": True,
            "data": categories
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve category data: {str(e)}"
        )


@router.get("/transcription-status")
async def get_transcription_status(
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get transcription status statistics.
    
    Returns:
        Transcribed vs non-transcribed audio statistics
    """
    try:
        logger.info("Fetching transcription status")
        
        status = await StatisticsService.get_transcription_status(db)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error fetching transcription status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve transcription status: {str(e)}"
        )


@router.get("/daily")
async def get_daily_transcriptions(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get daily transcription statistics.
    
    Args:
        days: Number of days to retrieve (default: 30, max: 365)
        
    Returns:
        Daily transcription trends
    """
    try:
        logger.info(f"Fetching daily transcriptions for {days} days")
        
        daily_data = await StatisticsService.get_daily_transcriptions(db, days)
        
        return {
            "success": True,
            "data": daily_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching daily transcriptions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve daily transcriptions: {str(e)}"
        )


@router.get("/admin-contributions")
async def get_admin_contributions(
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get contribution statistics by admin.
    
    Returns:
        List of admin contributions
    """
    try:
        logger.info("Fetching admin contributions")
        
        contributions = await StatisticsService.get_admin_contributions(db)
        
        return {
            "success": True,
            "data": contributions
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin contributions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve admin contributions: {str(e)}"
        )


@router.get("/audio-distribution")
async def get_audio_distribution(
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get audio duration distribution statistics.
    
    Returns:
        Distribution of audio clips by duration ranges
    """
    try:
        logger.info("Fetching audio distribution")
        
        distribution = await StatisticsService.get_audio_distribution(db)
        
        return {
            "success": True,
            "data": distribution
        }
        
    except Exception as e:
        logger.error(f"Error fetching audio distribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audio distribution: {str(e)}"
        )
