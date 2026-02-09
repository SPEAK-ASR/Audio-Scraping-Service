"""
Video management routes for querying and deleting videos.

This module contains routes for managing videos based on clip counts
and transcription status, including bulk deletion operations.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_database_session
from app.services.database_service import DatabaseService
from app.services.cloud_storage import CloudStorageService
from app.schemas.video_schemas import (
    LowClipVideosResponse,
    DeleteVideosRequest,
    DeleteVideosResponse,
    VideoMetadata,
    DeletedVideoInfo
)
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/videos", tags=["Video Management"])

# Service will be initialized lazily
cloud_storage_service = None


def get_cloud_storage_service():
    """Get or create cloud storage service instance."""
    global cloud_storage_service
    if cloud_storage_service is None:
        cloud_storage_service = CloudStorageService()
    return cloud_storage_service


@router.get("/low-clips", response_model=LowClipVideosResponse)
async def get_low_clip_videos(
    min_num: int = Query(..., ge=0, description="Minimum number of clips threshold"),
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Get all videos that have less than min_num clips and have 0 transcription count.
    
    This endpoint is useful for identifying videos that need more processing or
    may have issues with their audio splitting.
    
    Args:
        min_num: Minimum number of clips threshold (videos with fewer clips will be returned)
        db: Database session
        
    Returns:
        List of videos with their metadata and clip counts
    """
    try:
        logger.info(f"Fetching videos with < {min_num} clips and 0 transcriptions")
        
        # Get videos matching criteria
        videos = await DatabaseService.get_videos_with_low_clips(db, min_num)
        
        # Extract video IDs
        video_ids = [v['video_id'] for v in videos]
        
        # Format metadata
        metadata = [
            VideoMetadata(
                video_id=v['video_id'],
                num_of_clips=v['num_of_clips'],
                domain=v['domain'],
                title=v['title'],
                url=v['url'],
                uploader=v['uploader'],
                duration=v['duration']
            )
            for v in videos
        ]
        
        logger.info(f"Found {len(videos)} videos matching criteria")
        
        return LowClipVideosResponse(
            video_ids=video_ids,
            total_count=len(videos),
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Error fetching low clip videos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch videos: {str(e)}"
        )


@router.delete("/bulk-delete", response_model=DeleteVideosResponse)
async def delete_videos_bulk(
    request: DeleteVideosRequest,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Delete multiple videos and all their associated audio clips.
    
    This endpoint will:
    1. Delete all audio clip records from the database
    2. Delete video records from the database
    3. Delete all audio files from Google Cloud Storage
    
    Args:
        request: Request containing list of video IDs to delete
        db: Database session
        
    Returns:
        Summary of deletion operation including successes and failures
    """
    try:
        logger.info(f"Starting bulk deletion for {len(request.video_ids)} videos")
        
        storage_service = get_cloud_storage_service()
        
        deleted_videos = []
        failed_videos = []
        total_clips_deleted = 0
        all_audio_files_to_delete = []
        
        # Process each video
        for video_id in request.video_ids:
            try:
                # Delete video and clips from database
                result = await DatabaseService.delete_video_and_clips(db, video_id)
                
                if result['success']:
                    video_info = result['video_info']
                    audio_files = result['audio_files']
                    
                    deleted_videos.append(
                        DeletedVideoInfo(
                            video_id=video_info['video_id'],
                            video_link=video_info['video_link'],
                            domain=video_info['domain'],
                            num_clips_deleted=video_info['num_clips']
                        )
                    )
                    
                    total_clips_deleted += video_info['num_clips']
                    all_audio_files_to_delete.extend(audio_files)
                    
                    logger.info(f"Successfully deleted video {video_id} with {video_info['num_clips']} clips")
                else:
                    failed_videos.append({
                        'video_id': video_id,
                        'error': result.get('error', 'Unknown error')
                    })
                    logger.error(f"Failed to delete video {video_id}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error deleting video {video_id}: {e}", exc_info=True)
                failed_videos.append({
                    'video_id': video_id,
                    'error': str(e)
                })
        
        # Delete audio files from cloud storage
        cloud_deleted = 0
        cloud_failed = 0
        
        if all_audio_files_to_delete:
            logger.info(f"Deleting {len(all_audio_files_to_delete)} audio files from cloud storage")
            
            try:
                delete_result = storage_service.delete_files_batch(all_audio_files_to_delete)
                cloud_deleted = len(delete_result['successful'])
                cloud_failed = len(delete_result['failed'])
                
                logger.info(f"Cloud storage deletion: {cloud_deleted} successful, {cloud_failed} failed")
            except Exception as e:
                logger.error(f"Error during cloud storage deletion: {e}", exc_info=True)
                cloud_failed = len(all_audio_files_to_delete)
        
        # Prepare response
        response = DeleteVideosResponse(
            total_deleted=len(deleted_videos),
            total_failed=len(failed_videos),
            deleted_videos=deleted_videos,
            failed_videos=failed_videos if failed_videos else None,
            total_clips_deleted=total_clips_deleted,
            total_cloud_files_deleted=cloud_deleted,
            total_cloud_files_failed=cloud_failed
        )
        
        logger.info(
            f"Bulk deletion complete: {len(deleted_videos)} videos deleted, "
            f"{len(failed_videos)} failed, {total_clips_deleted} clips deleted"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in bulk delete operation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete videos: {str(e)}"
        )
