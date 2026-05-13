"""
Database service for managing YouTube videos and audio clips.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError

from app.models.youtube_video import YouTubeVideo
from app.models.audio import Audio
from app.utils import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service for database operations related to YouTube videos and audio clips."""
    
    @staticmethod
    async def check_video_exists(db: AsyncSession, video_id: str) -> Optional[YouTubeVideo]:
        """
        Check if a YouTube video already exists in the database.
        
        Args:
            db: Database session
            video_id: YouTube video ID to check
            
        Returns:
            YouTubeVideo instance if exists, None otherwise
        """
        try:
            stmt = select(YouTubeVideo).where(YouTubeVideo.video_id == video_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error checking if video exists: {e}")
            raise
    
    @staticmethod
    async def check_videos_exist_batch(db: AsyncSession, video_ids: List[str]) -> List[str]:
        """
        Check which videos from a list already exist in the database.
        
        Args:
            db: Database session
            video_ids: List of YouTube video IDs to check
            
        Returns:
            List of video IDs that exist in the database
        """
        try:
            if not video_ids:
                return []
            
            stmt = select(YouTubeVideo.video_id).where(YouTubeVideo.video_id.in_(video_ids))
            result = await db.execute(stmt)
            existing_video_ids = result.scalars().all()
            return list(existing_video_ids)
        except Exception as e:
            logger.error(f"Error checking videos in batch: {e}")
            raise
    
    @staticmethod
    async def save_video_metadata(db: AsyncSession, metadata: Dict[str, Any]) -> YouTubeVideo:
        """
        Save YouTube video metadata to the database.
        
        Args:
            db: Database session
            metadata: Video metadata from YouTube (must include 'domain' field)
            
        Returns:
            Created YouTubeVideo instance
        """
        try:
            # Parse upload_date if it exists
            upload_date_obj = None
            if metadata.get('upload_date'):
                upload_date_str = metadata['upload_date']
                if isinstance(upload_date_str, str) and len(upload_date_str) == 8:
                    # Format: YYYYMMDD
                    year = int(upload_date_str[:4])
                    month = int(upload_date_str[4:6])
                    day = int(upload_date_str[6:8])
                    upload_date_obj = date(year, month, day)
            
            # Handle domain field - pass string directly to database
            domain_value = metadata.get('domain')
            if domain_value and not isinstance(domain_value, str):
                logger.warning(f"Domain value is not a string: {type(domain_value)}, setting to None")
                domain_value = None
            
            video = YouTubeVideo(
                video_id=metadata.get('video_id'),
                title=metadata.get('title'),
                description=metadata.get('description'),
                duration=metadata.get('duration'),
                uploader=metadata.get('uploader'),
                upload_date=upload_date_obj,
                thumbnail=metadata.get('thumbnail'),
                url=metadata.get('url'),
                domain=domain_value  # Pass string directly, PostgreSQL will validate
            )
            
            db.add(video)
            await db.commit()
            await db.refresh(video)
            
            logger.info(f"Successfully saved video metadata for video_id: {metadata.get('video_id')}")
            return video
            
        except IntegrityError as e:
            await db.rollback()
            if "unique constraint" in str(e).lower():
                logger.warning(f"Video {metadata.get('video_id')} already exists in database")
                # Try to get the existing video
                existing_video = await DatabaseService.check_video_exists(db, metadata.get('video_id'))
                if existing_video:
                    return existing_video
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving video metadata: {e}")
            raise
    
    @staticmethod
    async def save_audio_clip(
        db: AsyncSession,
        clip_data: Dict[str, Any],
        youtube_video_id: str,
        transcription: Optional[str] = None
    ) -> Audio:
        """
        Save audio clip data to the database.
        
        Args:
            db: Database session
            clip_data: Audio clip information
            youtube_video_id: UUID of the YouTube video this clip belongs to
            transcription: Optional Google transcription
            
        Returns:
            Created Audio instance
        """
        try:
            # Convert start_time and end_time to time objects
            from datetime import time
            start_time_obj = None
            end_time_obj = None
            
            if clip_data.get('start_time') is not None:
                try:
                    start_seconds = float(clip_data['start_time'])
                    total_seconds = int(start_seconds)
                    microseconds = int((start_seconds % 1) * 1000000)
                    
                    # Handle times that might exceed 24 hours by wrapping
                    hours = (total_seconds // 3600) % 24
                    minutes = (total_seconds % 3600) // 60
                    seconds_part = total_seconds % 60
                    
                    start_time_obj = time(
                        hour=hours,
                        minute=minutes,
                        second=seconds_part,
                        microsecond=microseconds
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert start_time {clip_data.get('start_time')}: {e}")
                    start_time_obj = None
            
            if clip_data.get('end_time') is not None:
                try:
                    end_seconds = float(clip_data['end_time'])
                    total_seconds = int(end_seconds)
                    microseconds = int((end_seconds % 1) * 1000000)
                    
                    # Handle times that might exceed 24 hours by wrapping
                    hours = (total_seconds // 3600) % 24
                    minutes = (total_seconds % 3600) // 60
                    seconds_part = total_seconds % 60
                    
                    end_time_obj = time(
                        hour=hours,
                        minute=minutes,
                        second=seconds_part,
                        microsecond=microseconds
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert end_time {clip_data.get('end_time')}: {e}")
                    end_time_obj = None
            
            audio = Audio(
                audio_filename=clip_data.get('clip_name'),
                google_transcription=transcription if transcription else "",  # Empty string instead of None
                transcription_count=0,  # Will be updated by database trigger
                start_time=start_time_obj,
                end_time=end_time_obj,
                padded_duration=clip_data.get('padded_duration'),
                youtube_video_id=youtube_video_id
            )
            
            db.add(audio)
            await db.commit()
            await db.refresh(audio)
            
            logger.info(f"Successfully saved audio clip: {clip_data.get('clip_name')}")
            return audio
            
        except IntegrityError as e:
            await db.rollback()
            if "unique constraint" in str(e).lower():
                logger.warning(f"Audio clip {clip_data.get('clip_name')} already exists in database")
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving audio clip: {e}")
            raise
    
    @staticmethod
    async def save_audio_clip_no_commit(
        db: AsyncSession,
        clip_data: Dict[str, Any],
        youtube_video_id: str,
        transcription: Optional[str] = None
    ) -> Audio:
        """
        Save audio clip data to the database WITHOUT committing.
        Used for batch operations where commit happens at the end.
        
        Args:
            db: Database session
            clip_data: Audio clip information
            youtube_video_id: UUID of the YouTube video this clip belongs to
            transcription: Optional Google transcription
            
        Returns:
            Created Audio instance (not yet committed)
        """
        try:
            # Convert start_time and end_time to time objects
            from datetime import time
            start_time_obj = None
            end_time_obj = None
            
            if clip_data.get('start_time') is not None:
                try:
                    start_seconds = float(clip_data['start_time'])
                    total_seconds = int(start_seconds)
                    microseconds = int((start_seconds % 1) * 1000000)
                    
                    # Handle times that might exceed 24 hours by wrapping
                    hours = (total_seconds // 3600) % 24
                    minutes = (total_seconds % 3600) // 60
                    seconds_part = total_seconds % 60
                    
                    start_time_obj = time(
                        hour=hours,
                        minute=minutes,
                        second=seconds_part,
                        microsecond=microseconds
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert start_time {clip_data.get('start_time')}: {e}")
                    start_time_obj = None
            
            if clip_data.get('end_time') is not None:
                try:
                    end_seconds = float(clip_data['end_time'])
                    total_seconds = int(end_seconds)
                    microseconds = int((end_seconds % 1) * 1000000)
                    
                    # Handle times that might exceed 24 hours by wrapping
                    hours = (total_seconds // 3600) % 24
                    minutes = (total_seconds % 3600) // 60
                    seconds_part = total_seconds % 60
                    
                    end_time_obj = time(
                        hour=hours,
                        minute=minutes,
                        second=seconds_part,
                        microsecond=microseconds
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert end_time {clip_data.get('end_time')}: {e}")
                    end_time_obj = None
            
            audio = Audio(
                audio_filename=clip_data.get('clip_name'),
                google_transcription=transcription if transcription else "",  # Empty string instead of None
                transcription_count=0,  # Will be updated by database trigger
                start_time=start_time_obj,
                end_time=end_time_obj,
                padded_duration=clip_data.get('padded_duration'),
                youtube_video_id=youtube_video_id
            )
            
            db.add(audio)
            # Flush to get the ID but don't commit yet
            await db.flush()
            
            logger.info(f"Prepared audio clip for batch commit: {clip_data.get('clip_name')}")
            return audio
            
        except Exception as e:
            logger.error(f"Error preparing audio clip: {e}")
            raise
    
    @staticmethod
    async def get_video_audio_clips(db: AsyncSession, video_id: str) -> List[Audio]:
        """
        Get all audio clips for a specific YouTube video.
        
        Args:
            db: Database session
            video_id: YouTube video ID
            
        Returns:
            List of Audio instances
        """
        try:
            # First get the video
            video = await DatabaseService.check_video_exists(db, video_id)
            if not video:
                return []
            
            # Get all audio clips for this video
            stmt = select(Audio).where(Audio.youtube_video_id == video.id)
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting video audio clips: {e}")
            raise
    
    @staticmethod
    async def get_videos_with_low_clips(
        db: AsyncSession, 
        min_num_clips: int
    ) -> List[Dict[str, Any]]:
        """
        Get all videos that have less than min_num clips and have 0 transcription count.
        
        Args:
            db: Database session
            min_num_clips: Minimum number of clips threshold
            
        Returns:
            List of video metadata dictionaries with clip counts
        """
        try:
            # Query to get videos with clip count less than min_num 
            # and all their clips have transcription_count = 0
            from sqlalchemy import outerjoin
            
            # Subquery to count clips per video
            clip_count_subquery = (
                select(
                    Audio.youtube_video_id,
                    func.count(Audio.audio_id).label('clip_count'),
                    func.sum(Audio.transcription_count).label('total_transcription_count')
                )
                .group_by(Audio.youtube_video_id)
                .subquery()
            )
            
            # Main query to get videos matching criteria
            stmt = (
                select(
                    YouTubeVideo,
                    func.coalesce(clip_count_subquery.c.clip_count, 0).label('num_clips'),
                    func.coalesce(clip_count_subquery.c.total_transcription_count, 0).label('total_trans_count')
                )
                .outerjoin(clip_count_subquery, YouTubeVideo.id == clip_count_subquery.c.youtube_video_id)
                .where(
                    func.coalesce(clip_count_subquery.c.clip_count, 0) < min_num_clips
                )
                .where(
                    func.coalesce(clip_count_subquery.c.total_transcription_count, 0) == 0
                )
            )
            
            result = await db.execute(stmt)
            rows = result.all()
            
            # Format results
            videos = []
            for row in rows:
                video = row[0]  # YouTubeVideo object
                num_clips = row[1]  # clip count
                
                videos.append({
                    'video_id': video.video_id,
                    'num_of_clips': num_clips,
                    'domain': video.domain,
                    'title': video.title,
                    'url': video.url,
                    'uploader': video.uploader,
                    'duration': video.duration,
                    'created_at': video.created_at.isoformat() if video.created_at else None
                })
            
            logger.info(f"Found {len(videos)} videos with < {min_num_clips} clips and 0 transcriptions")
            return videos
            
        except Exception as e:
            logger.error(f"Error getting videos with low clips: {e}")
            raise
    
    @staticmethod
    async def delete_video_and_clips(
        db: AsyncSession, 
        video_id: str
    ) -> Dict[str, Any]:
        """
        Delete a video and all its associated audio clips from the database.
        Also returns information about the clips for cloud storage deletion.
        
        Args:
            db: Database session
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video info and list of audio filenames to delete from cloud
        """
        try:
            # Get the video
            video = await DatabaseService.check_video_exists(db, video_id)
            if not video:
                return {
                    'success': False,
                    'error': f'Video {video_id} not found',
                    'audio_files': []
                }
            
            # Get all audio clips for this video
            audio_clips = await DatabaseService.get_video_audio_clips(db, video_id)
            
            video_info = {
                'video_id': video.video_id,
                'video_link': video.url,
                'domain': video.domain,
                'num_clips': len(audio_clips)
            }
            
            # Collect audio filenames for cloud storage deletion
            audio_files = [clip.audio_filename for clip in audio_clips]
            
            # Delete audio clips first (due to foreign key constraint)
            delete_audio_stmt = delete(Audio).where(Audio.youtube_video_id == video.id)
            await db.execute(delete_audio_stmt)
            
            # Delete the video
            delete_video_stmt = delete(YouTubeVideo).where(YouTubeVideo.id == video.id)
            await db.execute(delete_video_stmt)
            
            # Commit the transaction
            await db.commit()
            
            logger.info(f"Deleted video {video_id} and {len(audio_files)} audio clips")
            
            return {
                'success': True,
                'video_info': video_info,
                'audio_files': audio_files
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting video {video_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_files': []
            }
