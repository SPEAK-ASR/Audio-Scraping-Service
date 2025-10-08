"""
YouTube video processing routes.

This module contains all routes related to YouTube video processing,
including downloading, splitting, transcription, and cloud storage operations.
"""

import uuid
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_database_session
from app.services.youtube_processor import YouTubeProcessor
from app.services.transcription_service import TranscriptionService
from app.services.cloud_storage import CloudStorageService
from app.models.audio import Audio
from app.models.youtube_video import YouTubeVideo
from app.services.database_service import DatabaseService
from app.schemas.audio_schemas import (
    AudioProcessingRequest, AudioProcessingResponse,
    AudioSplitRequest, AudioSplitResponse,
    TranscriptionRequest, TranscriptionResponse, TranscribedClip,
    CloudStorageRequest, CloudStorageResponse,
    VideoExistenceResponse, VideoIdExtractionRequest, VideoIdExtractionResponse
)
from app.utils import get_logger

# Setup logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["YouTube Processing"])

# Services will be initialized lazily to avoid GCP auth issues during import
youtube_processor = None
transcription_service = None
cloud_storage_service = None


def get_youtube_processor():
    """Get or create YouTube processor instance."""
    global youtube_processor
    if youtube_processor is None:
        youtube_processor = YouTubeProcessor()
    return youtube_processor


def get_transcription_service():
    """Get or create transcription service instance."""
    global transcription_service
    if transcription_service is None:
        transcription_service = TranscriptionService()
    return transcription_service


def get_cloud_storage_service():
    """Get or create cloud storage service instance."""
    global cloud_storage_service
    if cloud_storage_service is None:
        cloud_storage_service = CloudStorageService()
    return cloud_storage_service


@router.post("/split-audio", response_model=AudioSplitResponse)
async def split_youtube_audio(
    request: AudioSplitRequest,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Step 1: Download YouTube video and split into audio clips using VAD.
    
    Args:
        request: Parameters for audio splitting including YouTube URL and VAD settings
        db: Database session for duplicate checking
        
    Returns:
        Video metadata and information about created audio clips
    """
    try:
        logger.info(f"Starting audio splitting for YouTube video", extra={
            "url": str(request.youtube_url),
            "vad_aggressiveness": request.vad_aggressiveness,
            "start_padding": request.start_padding,
            "end_padding": request.end_padding
        })
        
        # Create base directory for processing
        base_dir = Path.cwd()
        
        # Extract video ID for duplicate checking
        video_id = get_youtube_processor().extract_video_id(str(request.youtube_url))
        
        # Check if video already exists in database
        try:
            existing_video = await DatabaseService.check_video_exists(db, video_id)
            if existing_video:
                logger.info(f"Video {video_id} already exists in database with title: {existing_video.title}")
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "VIDEO_ALREADY_EXISTS",
                        "message": f"Video with ID '{video_id}' has already been processed and exists in the database.",
                        "video_title": existing_video.title,
                        "video_id": video_id,
                        "suggestion": "Use the existing video data or delete it first if you want to reprocess."
                    }
                )
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"Database error while checking video existence: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Database connection error: {str(db_error)}. Please check if the database is running and accessible."
            )
        
        # Download and split audio
        video_metadata, clips_data = await get_youtube_processor().process_video(
            url=str(request.youtube_url),
            output_dir=base_dir,
            vad_aggressiveness=request.vad_aggressiveness,
            start_padding=request.start_padding,
            end_padding=request.end_padding
        )
        
        logger.info(f"Successfully created {len(clips_data)} audio clips for video {video_id}")
        
        # Save metadata files for use in subsequent steps
        clips_dir = base_dir / "output" / video_id
        if clips_dir.exists():
            try:
                import json
                
                # Save video metadata
                video_metadata_file = clips_dir / "video_metadata.json"
                with open(video_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(video_metadata, f, indent=2, ensure_ascii=False)
                
                # Save clip metadata (convert clips_data to dict keyed by clip_name)
                clip_metadata = {}
                for clip in clips_data:
                    clip_metadata[clip['clip_name']] = clip
                
                clip_metadata_file = clips_dir / "clip_metadata.json"
                with open(clip_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(clip_metadata, f, indent=2, ensure_ascii=False)
                
                logger.info("Saved metadata files for subsequent processing steps")
            except Exception as e:
                logger.warning(f"Failed to save metadata files: {e}")
        
        return AudioSplitResponse(
            success=True,
            message=f"Successfully split audio into {len(clips_data)} clips",
            video_id=video_id,
            video_metadata=video_metadata,
            clips=clips_data,
            total_clips=len(clips_data),
            start_padding=request.start_padding,
            end_padding=request.end_padding
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio splitting failed", extra={
            "url": str(request.youtube_url),
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio splitting failed: {str(e)}")


@router.post("/transcribe-clips", response_model=TranscriptionResponse)
async def transcribe_audio_clips(
    request: TranscriptionRequest
):
    """
    Step 2: Get Google transcriptions for existing audio clips.
    
    Args:
        request: Video ID and optional list of specific clip names to transcribe
        
    Returns:
        Transcription results for the processed clips
    """
    try:
        logger.info(f"Starting transcription for video {request.video_id}", extra={
            "video_id": request.video_id,
            "clip_names": request.clip_names
        })
        
        # Find clips directory
        base_dir = Path.cwd()
        clips_dir = base_dir / "output" / request.video_id
        
        if not clips_dir.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Clips directory not found for video {request.video_id}. Run split-audio first."
            )
        
        # Get list of clips to process
        if request.clip_names:
            clip_files = [clips_dir / clip_name for clip_name in request.clip_names]
            # Verify all requested clips exist
            for clip_file in clip_files:
                if not clip_file.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Clip file not found: {clip_file.name}"
                    )
        else:
            # Process all .wav files in the directory
            clip_files = list(clips_dir.glob("*.wav"))
            if not clip_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"No audio clips found in directory for video {request.video_id}"
                )
        
        transcribed_clips = []
        failed_clips = []
        
        for clip_file in clip_files:
            try:
                transcription = await get_transcription_service().transcribe_audio(str(clip_file))
                # Handle case where transcription service returns None or empty string
                if transcription is None or transcription.strip() == "":
                    logger.warning(f"Transcription service returned empty result for {clip_file.name}")
                    transcription = None
                
                transcribed_clips.append(TranscribedClip(
                    clip_name=clip_file.name,
                    transcription=transcription
                ))
                logger.info(f"Successfully processed transcription for {clip_file.name}")
            except Exception as e:
                logger.error(f"Transcription failed for {clip_file.name}: {e}")
                # Add failed clips to both failed list and transcribed list with None transcription
                failed_clips.append(clip_file.name)
                transcribed_clips.append(TranscribedClip(
                    clip_name=clip_file.name,
                    transcription=None
                ))
        
        # Count successful transcriptions (those with non-null transcription)
        successful_count = sum(1 for clip in transcribed_clips if clip.transcription is not None)
        
        # Save transcriptions to file for use in save-clips step
        try:
            import json
            transcription_data = {}
            for clip in transcribed_clips:
                transcription_data[clip.clip_name] = clip.transcription
            
            transcription_file = clips_dir / "transcriptions.json"
            with open(transcription_file, 'w', encoding='utf-8') as f:
                json.dump(transcription_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved transcriptions to file: {transcription_file}")
        except Exception as e:
            logger.warning(f"Failed to save transcriptions to file: {e}")
        
        return TranscriptionResponse(
            success=True,
            message=f"Successfully transcribed {successful_count} clips, {len(failed_clips)} failed",
            video_id=request.video_id,
            transcribed_clips=transcribed_clips,
            total_transcribed=successful_count,
            failed_clips=failed_clips
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription processing failed", extra={
            "video_id": request.video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription processing failed: {str(e)}")


@router.post("/save-clips", response_model=CloudStorageResponse)
async def save_clips_to_cloud_and_database(
    request: CloudStorageRequest,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Step 3: Save processed clips to cloud storage and add data to database.
    
    Args:
        request: Video ID, clip names, and storage/database options
        db: Database session
        
    Returns:
        Results of cloud storage and database operations
    """
    try:
        logger.info(f"Starting cloud storage and database operations for video {request.video_id}", extra={
            "video_id": request.video_id,
            "clip_names": request.clip_names,
            "upload_to_cloud": request.upload_to_cloud_bucket,
            "add_to_database": request.add_to_transcription_service
        })
        
        if not request.upload_to_cloud_bucket and not request.add_to_transcription_service:
            raise HTTPException(
                status_code=400,
                detail="At least one of upload_to_cloud_bucket or add_to_transcription_service must be true"
            )
        
        # Find clips directory
        base_dir = Path.cwd()
        clips_dir = base_dir / "output" / request.video_id
        
        if not clips_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Clips directory not found for video {request.video_id}. Run split-audio first."
            )
        
        # Get list of clips to process
        if request.clip_names:
            clip_files = [clips_dir / clip_name for clip_name in request.clip_names]
            # Verify all requested clips exist
            for clip_file in clip_files:
                if not clip_file.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Clip file not found: {clip_file.name}"
                    )
        else:
            # Process all .wav files in the directory
            clip_files = list(clips_dir.glob("*.wav"))
            if not clip_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"No audio clips found in directory for video {request.video_id}"
                )
        
        # Load clip metadata from the output directory
        clip_metadata = {}
        metadata_file = clips_dir / "clip_metadata.json"
        if metadata_file.exists():
            try:
                import json
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    clip_metadata = json.load(f)
                logger.info(f"Loaded clip metadata for {len(clip_metadata)} clips")
            except Exception as e:
                logger.warning(f"Failed to load clip metadata: {e}")
        
        # Load transcriptions - use provided transcriptions first, then file
        transcriptions = {}
        if request.transcriptions:
            transcriptions = request.transcriptions
            logger.info(f"Using provided transcriptions for {len(transcriptions)} clips")
        else:
            # Load from file if available
            transcription_file = clips_dir / "transcriptions.json"
            if transcription_file.exists():
                try:
                    import json
                    with open(transcription_file, 'r', encoding='utf-8') as f:
                        transcriptions = json.load(f)
                    logger.info(f"Loaded transcriptions for {len(transcriptions)} clips from file")
                except Exception as e:
                    logger.warning(f"Failed to load transcriptions: {e}")
        
        # Get video metadata - try to get from metadata file first, then re-fetch from YouTube
        video_metadata = None
        video_metadata_file = clips_dir / "video_metadata.json"
        if video_metadata_file.exists():
            try:
                import json
                with open(video_metadata_file, 'r', encoding='utf-8') as f:
                    video_metadata = json.load(f)
                logger.info("Loaded video metadata from file")
            except Exception as e:
                logger.warning(f"Failed to load video metadata from file: {e}")
        
        # If no metadata file, re-fetch from YouTube URL
        if not video_metadata:
            try:
                youtube_url = f"https://www.youtube.com/watch?v={request.video_id}"
                logger.info(f"Re-fetching video metadata from YouTube for {request.video_id}")
                video_metadata, _ = await get_youtube_processor().get_video_info(youtube_url)
            except Exception as e:
                logger.warning(f"Failed to re-fetch video metadata: {e}")
                # Create minimal metadata as fallback
                video_metadata = {
                    'video_id': request.video_id,
                    'title': f'Video {request.video_id}',
                    'url': f'https://youtube.com/watch?v={request.video_id}'
                }
        
        processed_clips = []
        failed_clips = []
        
        for clip_file in clip_files:
            try:
                clip_result = {
                    "clip_name": clip_file.name,
                    "cloud_url": None,
                    "database_id": None
                }
                
                # Upload to cloud storage if requested
                if request.upload_to_cloud_bucket:
                    try:
                        cloud_url = await get_cloud_storage_service().upload_audio_file(
                            file_path=str(clip_file),
                            blob_name=clip_file.name
                        )
                        clip_result["cloud_url"] = cloud_url
                        logger.info(f"Uploaded {clip_file.name} to cloud storage")
                    except Exception as e:
                        logger.error(f"Cloud upload failed for {clip_file.name}: {e}")
                        raise
                
                # Save to database if requested
                if request.add_to_transcription_service:
                    try:
                        # Get transcription if available
                        transcription = transcriptions.get(clip_file.name, None)
                        
                        # First, we need to get or create the YouTube video record
                        existing_video = await DatabaseService.check_video_exists(db, request.video_id)
                        if not existing_video and video_metadata:
                            logger.info(f"Creating new video record for {request.video_id}")
                            existing_video = await DatabaseService.save_video_metadata(db, video_metadata)
                        elif not existing_video:
                            logger.warning(f"No video metadata available for {request.video_id}")
                            # Create minimal fallback record
                            fallback_metadata = {
                                'video_id': request.video_id,
                                'title': f'Video {request.video_id}',
                                'url': f'https://youtube.com/watch?v={request.video_id}'
                            }
                            existing_video = await DatabaseService.save_video_metadata(db, fallback_metadata)
                        
                        # Get clip data from metadata or create defaults
                        clip_data = clip_metadata.get(clip_file.name, {
                            'clip_name': clip_file.name,
                            'start_time': 0,
                            'end_time': 0,
                            'duration': 0,
                            'padded_duration': 0
                        })
                        
                        # Ensure clip_name is set
                        clip_data['clip_name'] = clip_file.name
                        
                        audio_record = await DatabaseService.save_audio_clip(
                            db=db,
                            clip_data=clip_data,
                            youtube_video_id=existing_video.id,
                            transcription=transcription
                        )
                        
                        clip_result["database_id"] = str(audio_record.audio_id)
                        logger.info(f"Saved {clip_file.name} to database")
                    except Exception as e:
                        logger.error(f"Database save failed for {clip_file.name}: {e}")
                        raise
                
                processed_clips.append(clip_result)
                
            except Exception as e:
                logger.error(f"Processing failed for {clip_file.name}: {e}")
                failed_clips.append(clip_file.name)
        
        return CloudStorageResponse(
            success=True,
            message=f"Successfully processed {len(processed_clips)} clips",
            video_id=request.video_id,
            processed_clips=processed_clips,
            total_processed=len(processed_clips),
            failed_clips=failed_clips
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cloud storage and database processing failed", extra={
            "video_id": request.video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cloud storage and database processing failed: {str(e)}")


@router.post("/process-youtube", response_model=AudioProcessingResponse)
async def process_youtube_video(
    request: AudioProcessingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Process a YouTube video: download, split into clips, and optionally transcribe/upload.
    
    Args:
        request: Processing parameters including YouTube URL and options
        background_tasks: FastAPI background tasks for async processing
        db: Database session
        
    Returns:
        Processing status and results
    """
    try:
        logger.info(f"Starting YouTube video processing", extra={
            "url": str(request.youtube_url),
            "transcription": request.get_google_transcription,
            "cloud_upload": request.upload_to_cloud_bucket,
            "database_save": request.add_to_transcription_service
        })
        
        # Create base directory for processing
        base_dir = Path.cwd()
        
        # Extract video ID for duplicate checking
        video_id = get_youtube_processor().extract_video_id(str(request.youtube_url))
        
        # Check if video already exists in database
        existing_video = await DatabaseService.check_video_exists(db, video_id)
        if existing_video:
            raise HTTPException(
                status_code=409,
                detail=f"Video with ID '{video_id}' has already been processed and exists in the database. "
                       f"Title: '{existing_video.title}'"
            )
        
        # Step 1: Download and process YouTube video
        video_metadata, clips_data, is_new_video = await get_youtube_processor().process_video_with_database(
            url=str(request.youtube_url),
            output_dir=base_dir,
            db_session=db,
            check_existing=True,
            vad_aggressiveness=request.vad_aggressiveness,
            start_padding=request.start_padding,
            end_padding=request.end_padding
        )
        
        if not is_new_video:
            raise HTTPException(
                status_code=409,
                detail=f"Video with ID '{video_id}' has already been processed."
            )
        
        logger.info(f"Successfully created {len(clips_data)} audio clips from video")
        logger.info(f"Clips data sample: {clips_data[:2] if clips_data else 'No clips generated'}")
        
        # Step 2: Save video metadata to database
        saved_video = await DatabaseService.save_video_metadata(db, video_metadata)
        logger.info(f"Saved video metadata to database with ID: {saved_video.id}")
        
        # Step 3: Process each clip based on options
        processed_clips = []
        
        for clip_data in clips_data:
            clip_path = Path(clip_data['clip_path'])
            
            # Initialize clip result
            clip_result = {
                'clip_name': clip_data['clip_name'],
                'duration': clip_data['duration'],
                'start_time': clip_data['start_time'],
                'end_time': clip_data['end_time'],
                'transcription': None,
                'cloud_url': None,
                'database_id': None,
                'clip_path': clip_data.get('clip_path', str(clip_path)),  # Local file path
                'audio_url': f"/output/{video_id}/{clip_data['clip_name']}"  # HTTP URL for frontend
            }
            
            # Optional: Get Google transcription
            if request.get_google_transcription:
                try:
                    transcription = await get_transcription_service().transcribe_audio(str(clip_path))
                    clip_result['transcription'] = transcription
                    logger.info(f"Transcribed {clip_data['clip_name']}")
                except Exception as e:
                    logger.error(f"Transcription failed for {clip_data['clip_name']}: {e}")
            
            # Optional: Upload to cloud bucket
            if request.upload_to_cloud_bucket:
                try:
                    cloud_url = await get_cloud_storage_service().upload_audio_file(
                        file_path=str(clip_path),
                        blob_name=clip_data['clip_name']
                    )
                    clip_result['cloud_url'] = cloud_url
                    logger.info(f"Uploaded {clip_data['clip_name']} to cloud storage")
                except Exception as e:
                    logger.error(f"Cloud upload failed for {clip_data['clip_name']}: {e}")
            
            # Optional: Save to database with proper foreign key relationship
            if request.add_to_transcription_service:
                try:
                    audio_record = await DatabaseService.save_audio_clip(
                        db=db,
                        clip_data=clip_data,
                        youtube_video_id=saved_video.id,
                        transcription=clip_result['transcription']
                    )
                    
                    clip_result['database_id'] = str(audio_record.audio_id)
                    logger.info(f"Saved {clip_data['clip_name']} to database")
                except Exception as e:
                    logger.error(f"Database save failed for {clip_data['clip_name']}: {e}")
            
            processed_clips.append(clip_result)
        
        logger.info(f"Final processed clips count: {len(processed_clips)}")
        if processed_clips:
            logger.info(f"Sample processed clip: {processed_clips[0]}")
        
        response = AudioProcessingResponse(
            success=True,
            message=f"Successfully processed {len(processed_clips)} clips from new video",
            video_metadata=video_metadata,
            clips=processed_clips,
            total_clips=len(processed_clips)
        )
        
        logger.info(f"Returning response with {len(response.clips)} clips")
        return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video processing failed", extra={
            "url": str(request.youtube_url),
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/extract-video-id", response_model=VideoIdExtractionResponse)
async def extract_video_id_from_url(request: VideoIdExtractionRequest):
    """
    Extract YouTube video ID from a URL.
    
    Args:
        request: Dictionary containing 'url' key with YouTube URL
        
    Returns:
        Extracted video ID
    """
    try:
        video_id = get_youtube_processor().extract_video_id(str(request.url))
        
        return VideoIdExtractionResponse(
            success=True,
            video_id=video_id,
            url=str(request.url)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error extracting video ID", extra={
            "url": str(request.url),
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error extracting video ID: {str(e)}")


@router.get("/check-video/{video_id}", response_model=VideoExistenceResponse)
async def check_video_exists(
    video_id: str,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Check if a YouTube video already exists in the database.
    
    Args:
        video_id: YouTube video ID to check
        db: Database session
        
    Returns:
        Information about whether the video exists and its details
    """
    try:
        logger.info(f"Checking if video {video_id} exists in database")
        
        existing_video = await DatabaseService.check_video_exists(db, video_id)
        
        if existing_video:
            # Get associated audio clips
            audio_clips = await DatabaseService.get_video_audio_clips(db, video_id)
            
            return VideoExistenceResponse(
                exists=True,
                video_details={
                    "id": str(existing_video.id),
                    "video_id": existing_video.video_id,
                    "title": existing_video.title,
                    "description": existing_video.description,
                    "duration": existing_video.duration,
                    "uploader": existing_video.uploader,
                    "upload_date": existing_video.upload_date.isoformat() if existing_video.upload_date else None,
                    "created_at": existing_video.created_at.isoformat(),
                    "url": existing_video.url
                },
                audio_clips_count=len(audio_clips),
                message=f"Video '{existing_video.title}' already exists in the database with {len(audio_clips)} audio clips."
            )
        else:
            return VideoExistenceResponse(
                exists=False,
                video_details=None,
                audio_clips_count=0,
                message=f"Video with ID '{video_id}' does not exist in the database."
            )
        
    except Exception as e:
        logger.error(f"Error checking video existence", extra={
            "video_id": video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking video existence: {str(e)}")


@router.get("/list-clips/{video_id}")
async def list_video_clips(video_id: str):
    """
    List all audio clips for a specific video ID.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        List of audio clips found on disk
    """
    try:
        logger.info(f"Listing clips for video {video_id}")
        
        # Find clips directory
        base_dir = Path.cwd()
        clips_dir = base_dir / "output" / video_id
        
        if not clips_dir.exists():
            return {
                "success": False,
                "video_id": video_id,
                "clips": [],
                "total_clips": 0,
                "message": f"No clips directory found for video {video_id}"
            }
        
        # Get all .wav files in the directory
        clip_files = list(clips_dir.glob("*.wav"))
        
        clips_info = []
        for clip_file in clip_files:
            clips_info.append({
                "clip_name": clip_file.name,
                "clip_path": str(clip_file),
                "audio_url": f"/output/{video_id}/{clip_file.name}",
                "file_size": clip_file.stat().st_size if clip_file.exists() else 0
            })
        
        return {
            "success": True,
            "video_id": video_id,
            "clips": clips_info,
            "total_clips": len(clips_info),
            "clips_directory": str(clips_dir),
            "message": f"Found {len(clips_info)} clips for video {video_id}"
        }
        
    except Exception as e:
        logger.error(f"Error listing clips", extra={
            "video_id": video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing clips: {str(e)}")


@router.post("/clean-transcriptions/{video_id}")
async def clean_null_transcriptions(video_id: str):
    """
    Delete audio files with null transcriptions and update metadata files.
    
    This endpoint:
    1. Identifies audio files with null/empty transcriptions
    2. Deletes those audio files from disk
    3. Removes entries from transcriptions.json
    4. Removes entries from clip_metadata.json
    
    Args:
        video_id: The video ID to clean
        
    Returns:
        Cleanup status with list of deleted files
    """
    try:
        logger.info(f"Starting cleanup of null transcriptions for video {video_id}")
        
        # Find clips directory
        base_dir = Path.cwd()
        clips_dir = base_dir / "output" / video_id
        
        if not clips_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Clips directory not found for video {video_id}"
            )
        
        # Load transcriptions.json
        transcription_file = clips_dir / "transcriptions.json"
        if not transcription_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Transcriptions file not found for video {video_id}"
            )
        
        import json
        
        # Read transcriptions
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcriptions = json.load(f)
        
        # Identify clips with null transcriptions
        null_clips = [clip_name for clip_name, transcription in transcriptions.items() 
                     if transcription is None or (isinstance(transcription, str) and transcription.strip() == '')]
        
        if not null_clips:
            return {
                "success": True,
                "message": "No null transcriptions found",
                "video_id": video_id,
                "deleted_files": [],
                "total_deleted": 0
            }
        
        logger.info(f"Found {len(null_clips)} clips with null transcriptions: {null_clips}")
        
        # Delete audio files with null transcriptions
        deleted_files = []
        for clip_name in null_clips:
            clip_path = clips_dir / clip_name
            if clip_path.exists():
                try:
                    clip_path.unlink()  # Delete the file
                    deleted_files.append(clip_name)
                    logger.info(f"Deleted audio file: {clip_name}")
                except Exception as e:
                    logger.error(f"Failed to delete {clip_name}: {e}")
        
        # Update transcriptions.json - remove null entries
        updated_transcriptions = {k: v for k, v in transcriptions.items() 
                                 if k not in null_clips}
        
        with open(transcription_file, 'w', encoding='utf-8') as f:
            json.dump(updated_transcriptions, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated transcriptions.json - removed {len(null_clips)} entries")
        
        # Update clip_metadata.json - remove entries for deleted clips
        clip_metadata_file = clips_dir / "clip_metadata.json"
        if clip_metadata_file.exists():
            try:
                with open(clip_metadata_file, 'r', encoding='utf-8') as f:
                    clip_metadata = json.load(f)
                
                # Remove entries for deleted clips
                updated_clip_metadata = {k: v for k, v in clip_metadata.items() 
                                        if k not in null_clips}
                
                with open(clip_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_clip_metadata, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Updated clip_metadata.json - removed {len(null_clips)} entries")
            except Exception as e:
                logger.warning(f"Failed to update clip_metadata.json: {e}")
        
        logger.info(f"Successfully cleaned {len(deleted_files)} files with null transcriptions")
        
        return {
            "success": True,
            "message": f"Successfully deleted {len(deleted_files)} clips with null transcriptions",
            "video_id": video_id,
            "deleted_files": deleted_files,
            "total_deleted": len(deleted_files),
            "remaining_clips": len(updated_transcriptions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup failed", extra={
            "video_id": video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.delete("/delete-audio/{video_id}")
async def delete_audio_files(video_id: str):
    """
    Delete all audio files for a specific video ID.
    
    Args:
        video_id: The video ID to delete files for
        
    Returns:
        Deletion status
    """
    try:
        logger.info(f"Starting audio file deletion for video {video_id}")
        
        # Find clips directory
        base_dir = Path.cwd()
        clips_dir = base_dir / "output" / video_id
        
        if not clips_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"No audio files found for video {video_id}"
            )
        
        # Count files before deletion
        audio_files = list(clips_dir.glob("*.wav"))
        file_count = len(audio_files)
        
        # Delete all audio files
        deleted_files = []
        for audio_file in audio_files:
            try:
                audio_file.unlink()  # Delete the file
                deleted_files.append(audio_file.name)
            except Exception as e:
                logger.error(f"Failed to delete {audio_file.name}: {e}")
        
        # Remove the directory if it's empty
        try:
            if clips_dir.exists() and not any(clips_dir.iterdir()):
                clips_dir.rmdir()
                logger.info(f"Removed empty directory: {clips_dir}")
        except Exception as e:
            logger.warning(f"Could not remove directory {clips_dir}: {e}")
        
        logger.info(f"Successfully deleted {len(deleted_files)} audio files for video {video_id}")
        
        return {
            "success": True,
            "message": f"Successfully deleted {len(deleted_files)} audio files",
            "video_id": video_id,
            "deleted_files": deleted_files,
            "total_deleted": len(deleted_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio file deletion failed", extra={
            "video_id": video_id,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio file deletion failed: {str(e)}")