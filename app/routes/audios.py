"""
Audio management routes for the Audio Scraping Service.

Provides endpoints for managing audio files including deletion operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from tqdm import tqdm

from app.core.database import get_async_database_session
from app.models.audio import Audio
from app.models.transcription import Transcription
from app.schemas.audio_schemas import AudioDeleteResponse
from app.services.cloud_storage import CloudStorageService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/audios",
    tags=["audios"]
)


@router.delete("/delete", response_model=AudioDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_audios(
    audio_filenames: List[str],
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Delete multiple audio files from database and cloud storage.
    
    This endpoint:
    - Checks if audio has transcriptions (skips deletion if transcription_count > 0)
    - Deletes audio record from database
    - Deletes audio file from cloud storage bucket
    - Shows progress as a progress bar in logging
    
    Args:
        audio_filenames: List of audio filenames to delete
        db: Database session
        
    Returns:
        AudioDeleteResponse with deletion results
        
    Example request body:
        [
            "UqdlylNhkBo-021.wav",
            "UqdlylNhkBo-020.wav"
        ]
    """
    logger.info(f"Starting deletion process for {len(audio_filenames)} audio files")
    
    deleted_audios = []
    failed_audios = []
    cloud_storage = CloudStorageService()
    
    # Create a progress bar for logging
    pbar = tqdm(total=len(audio_filenames), desc="Deleting audios", unit="file")
    
    for idx, audio_filename in enumerate(audio_filenames, 1):
        try:
            # Query audio record with transcription count
            result = await db.execute(
                select(Audio).where(Audio.audio_filename == audio_filename)
            )
            audio = result.scalar_one_or_none()
            
            if not audio:
                logger.warning(f"Audio not found in database: {audio_filename}")
                failed_audios.append({
                    "filename": audio_filename,
                    "reason": "Audio not found in database"
                })
                pbar.update(1)
                continue
            
            # Check if audio has transcriptions
            if audio.transcription_count > 0:
                logger.warning(f"Skipping {audio_filename}: has {audio.transcription_count} transcription(s)")
                failed_audios.append({
                    "filename": audio_filename,
                    "reason": f"Audio has {audio.transcription_count} transcription(s), cannot delete"
                })
                pbar.update(1)
                continue
            
            # Delete from cloud storage first
            # Assuming audio files are stored with their filename as blob name
            blob_deleted = cloud_storage.delete_file(audio_filename)
            
            if not blob_deleted:
                logger.warning(f"Failed to delete {audio_filename} from cloud storage")
                failed_audios.append({
                    "filename": audio_filename,
                    "reason": "Failed to delete from cloud storage"
                })
                pbar.update(1)
                continue
            
            # Delete from database
            await db.delete(audio)
            await db.flush()  # Flush to ensure deletion happens
            
            deleted_audios.append(audio_filename)
            logger.debug(f"Successfully deleted {audio_filename} ({idx}/{len(audio_filenames)})")
            
        except Exception as e:
            logger.error(f"Error deleting {audio_filename}: {str(e)}")
            failed_audios.append({
                "filename": audio_filename,
                "reason": f"Error: {str(e)}"
            })
        
        pbar.update(1)
    
    pbar.close()
    
    # Commit all deletions
    await db.commit()
    
    total_deleted = len(deleted_audios)
    total_failed = len(failed_audios)
    success = total_deleted > 0
    
    logger.info(f"Deletion complete: {total_deleted} deleted, {total_failed} failed")
    
    return AudioDeleteResponse(
        success=success,
        message=f"Deleted {total_deleted} audio file(s), {total_failed} failed",
        total_requested=len(audio_filenames),
        total_deleted=total_deleted,
        total_failed=total_failed,
        deleted_audios=deleted_audios,
        failed_audios=failed_audios
    )
