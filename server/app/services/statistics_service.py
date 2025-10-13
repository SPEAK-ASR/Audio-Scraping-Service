"""
Service for retrieving database statistics.
"""

from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import func, select, case, and_, cast, Date, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audio import Audio
from app.models.youtube_video import YouTubeVideo
from app.models.transcription import Transcription
from app.utils import get_logger

logger = get_logger(__name__)


class StatisticsService:
    """Service for calculating various database statistics."""
    
    @staticmethod
    async def get_category_durations(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get total duration by category using padded_duration from audio clips.
        
        Returns:
            List of dictionaries containing category statistics
        """
        try:
            # Query to get duration by category
            query = (
                select(
                    YouTubeVideo.domain.label('category'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('total_duration'),
                    func.count(Audio.audio_id.distinct()).label('clip_count'),
                    func.count(YouTubeVideo.id.distinct()).label('video_count')
                )
                .outerjoin(Audio, YouTubeVideo.id == Audio.youtube_video_id)
                .where(Audio.padded_duration.isnot(None))
                .group_by(YouTubeVideo.domain)
                .order_by(func.sum(Audio.padded_duration).desc())
            )
            
            result = await db.execute(query)
            rows = result.all()
            
            category_data = []
            for row in rows:
                category = row.category or 'uncategorized'
                total_seconds = float(row.total_duration or 0)
                
                category_data.append({
                    'category': category,
                    'total_duration_hours': total_seconds / 3600,
                    'total_duration_minutes': total_seconds / 60,
                    'clip_count': row.clip_count,
                    'video_count': row.video_count
                })
            
            logger.info(f"Retrieved category durations for {len(category_data)} categories")
            return category_data
            
        except Exception as e:
            logger.error(f"Error getting category durations: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_transcription_status(db: AsyncSession) -> Dict[str, Any]:
        """
        Get statistics on transcribed vs non-transcribed audios.
        
        Returns:
            Dictionary containing transcription status statistics
        """
        try:
            # Count transcribed audios (those with transcription records)
            transcribed_query = (
                select(
                    func.count(Audio.audio_id.distinct()).label('count'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('duration')
                )
                .join(Transcription, Audio.audio_id == Transcription.audio_id)
                .where(Audio.padded_duration.isnot(None))
            )
            
            transcribed_result = await db.execute(transcribed_query)
            transcribed_row = transcribed_result.first()
            
            # Count non-transcribed audios (those without transcription records)
            non_transcribed_query = (
                select(
                    func.count(Audio.audio_id).label('count'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('duration')
                )
                .outerjoin(Transcription, Audio.audio_id == Transcription.audio_id)
                .where(
                    and_(
                        Transcription.trans_id.is_(None),
                        Audio.padded_duration.isnot(None)
                    )
                )
            )
            
            non_transcribed_result = await db.execute(non_transcribed_query)
            non_transcribed_row = non_transcribed_result.first()
            
            transcribed_count = transcribed_row.count if transcribed_row else 0
            non_transcribed_count = non_transcribed_row.count if non_transcribed_row else 0
            total_count = transcribed_count + non_transcribed_count
            
            transcription_rate = (transcribed_count / total_count * 100) if total_count > 0 else 0
            
            transcribed_duration = float(transcribed_row.duration if transcribed_row else 0)
            non_transcribed_duration = float(non_transcribed_row.duration if non_transcribed_row else 0)
            
            status_data = {
                'transcribed_count': transcribed_count,
                'non_transcribed_count': non_transcribed_count,
                'transcribed_duration_hours': transcribed_duration / 3600,
                'non_transcribed_duration_hours': non_transcribed_duration / 3600,
                'total_count': total_count,
                'transcription_rate': round(transcription_rate, 2)
            }
            
            logger.info(f"Retrieved transcription status: {transcription_rate:.2f}% transcribed")
            return status_data
            
        except Exception as e:
            logger.error(f"Error getting transcription status: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_daily_transcriptions(db: AsyncSession, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily transcription statistics for the last N days.
        
        Args:
            db: Database session
            days: Number of days to retrieve (default 30)
            
        Returns:
            List of dictionaries containing daily statistics
        """
        try:
            # Calculate the cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get daily transcription counts
            query = (
                select(
                    cast(Transcription.created_at, Date).label('date'),
                    func.count(Transcription.trans_id).label('transcription_count'),
                    func.count(Audio.audio_id.distinct()).label('audio_count'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('total_duration')
                )
                .join(Audio, Transcription.audio_id == Audio.audio_id)
                .where(
                    and_(
                        Transcription.created_at >= cutoff_date,
                        Audio.padded_duration.isnot(None)
                    )
                )
                .group_by(cast(Transcription.created_at, Date))
                .order_by(cast(Transcription.created_at, Date).desc())
            )
            
            result = await db.execute(query)
            rows = result.all()
            
            daily_data = []
            for row in rows:
                total_seconds = float(row.total_duration or 0)
                daily_data.append({
                    'date': row.date,
                    'transcription_count': row.transcription_count,
                    'audio_count': row.audio_count,
                    'total_duration_hours': total_seconds / 3600
                })
            
            logger.info(f"Retrieved daily transcriptions for {len(daily_data)} days")
            return daily_data
            
        except Exception as e:
            logger.error(f"Error getting daily transcriptions: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_admin_contributions(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get contribution statistics by admin.
        Non-admin contributions are grouped together as 'non_admin'.
        
        Returns:
            List of dictionaries containing admin contribution statistics
        """
        try:
            # Get admin contributions
            query = (
                select(
                    case(
                        (Transcription.admin.isnot(None), cast(Transcription.admin, Text)),
                        else_='non_admin'
                    ).label('admin'),
                    func.count(Transcription.trans_id).label('transcription_count'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('total_duration')
                )
                .join(Audio, Transcription.audio_id == Audio.audio_id)
                .where(Audio.padded_duration.isnot(None))
                .group_by('admin')
                .order_by(func.count(Transcription.trans_id).desc())
            )
            
            result = await db.execute(query)
            rows = result.all()
            
            # Calculate total for percentage
            total_transcriptions = sum(row.transcription_count for row in rows)
            
            admin_data = []
            for row in rows:
                total_seconds = float(row.total_duration or 0)
                percentage = (row.transcription_count / total_transcriptions * 100) if total_transcriptions > 0 else 0
                
                admin_data.append({
                    'admin': row.admin,
                    'transcription_count': row.transcription_count,
                    'total_duration_hours': total_seconds / 3600,
                    'percentage': round(percentage, 2)
                })
            
            logger.info(f"Retrieved contributions from {len(admin_data)} admins")
            return admin_data
            
        except Exception as e:
            logger.error(f"Error getting admin contributions: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_total_summary(db: AsyncSession) -> Dict[str, Any]:
        """
        Get overall summary statistics.
        
        Returns:
            Dictionary containing summary statistics
        """
        try:
            # Total videos
            video_count_query = select(func.count(YouTubeVideo.id))
            video_result = await db.execute(video_count_query)
            total_videos = video_result.scalar() or 0
            
            # Total audio clips and duration
            audio_query = (
                select(
                    func.count(Audio.audio_id).label('count'),
                    func.coalesce(func.sum(Audio.padded_duration), 0).label('total_duration'),
                    func.coalesce(func.avg(Audio.padded_duration), 0).label('avg_duration')
                )
                .where(Audio.padded_duration.isnot(None))
            )
            audio_result = await db.execute(audio_query)
            audio_row = audio_result.first()
            
            # Total transcribed duration
            transcribed_duration_query = (
                select(func.coalesce(func.sum(Audio.padded_duration), 0))
                .join(Transcription, Audio.audio_id == Transcription.audio_id)
                .where(Audio.padded_duration.isnot(None))
            )
            transcribed_result = await db.execute(transcribed_duration_query)
            transcribed_duration = float(transcribed_result.scalar() or 0)
            
            # Total transcriptions count
            transcription_count_query = select(func.count(Transcription.trans_id))
            transcription_result = await db.execute(transcription_count_query)
            total_transcriptions = transcription_result.scalar() or 0
            
            total_duration = float(audio_row.total_duration if audio_row else 0)
            avg_duration = float(audio_row.avg_duration if audio_row else 0)
            
            summary = {
                'total_videos': total_videos,
                'total_audio_clips': audio_row.count if audio_row else 0,
                'total_duration_hours': total_duration / 3600,
                'transcribed_duration_hours': transcribed_duration / 3600,
                'total_transcriptions': total_transcriptions,
                'average_clip_duration_seconds': round(avg_duration, 2)
            }
            
            logger.info(f"Retrieved total summary: {total_videos} videos, {summary['total_audio_clips']} clips")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting total summary: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_all_statistics(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """
        Get all statistics in one call.
        
        Args:
            db: Database session
            days: Number of days for daily statistics
            
        Returns:
            Dictionary containing all statistics
        """
        try:
            logger.info("Fetching all statistics...")
            
            summary = await StatisticsService.get_total_summary(db)
            category_durations = await StatisticsService.get_category_durations(db)
            transcription_status = await StatisticsService.get_transcription_status(db)
            daily_transcriptions = await StatisticsService.get_daily_transcriptions(db, days)
            admin_contributions = await StatisticsService.get_admin_contributions(db)
            
            statistics = {
                'success': True,
                'message': 'Statistics retrieved successfully',
                'summary': summary,
                'category_durations': category_durations,
                'transcription_status': transcription_status,
                'daily_transcriptions': daily_transcriptions,
                'admin_contributions': admin_contributions
            }
            
            logger.info("Successfully retrieved all statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting all statistics: {e}", exc_info=True)
            raise
