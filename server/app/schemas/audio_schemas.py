"""
Pydantic schemas for API request/response models.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class AudioProcessingRequest(BaseModel):
    """Request model for YouTube audio processing."""
    
    youtube_url: HttpUrl = Field(..., description="YouTube video URL to process")
    get_google_transcription: bool = Field(default=False, description="Whether to transcribe audio using Google Speech-to-Text")
    upload_to_cloud_bucket: bool = Field(default=False, description="Whether to upload clips to Google Cloud Storage")
    add_to_transcription_service: bool = Field(default=False, description="Whether to save clips data to database")
    
    # VAD and processing parameters
    vad_aggressiveness: int = Field(default=2, ge=0, le=3, description="VAD aggressiveness level (0-3)")
    start_padding: float = Field(default=1.0, ge=0, le=5.0, description="Silent padding in seconds to add to beginning of clips")
    end_padding: float = Field(default=0.5, ge=0, le=5.0, description="Silent padding in seconds to add to end of clips")


# New schemas for separate processing steps

class AudioSplitRequest(BaseModel):
    """Request model for YouTube audio splitting only."""
    
    youtube_url: HttpUrl = Field(..., description="YouTube video URL to process")
    vad_aggressiveness: int = Field(default=2, ge=0, le=3, description="VAD aggressiveness level (0-3)")
    start_padding: float = Field(default=1.0, ge=0, le=5.0, description="Silent padding in seconds to add to beginning of clips")
    end_padding: float = Field(default=0.5, ge=0, le=5.0, description="Silent padding in seconds to add to end of clips")


class TranscriptionRequest(BaseModel):
    """Request model for batch transcription of audio clips."""
    
    video_id: str = Field(..., description="Video ID to process clips for")
    clip_names: Optional[List[str]] = Field(default=None, description="Specific clip names to transcribe. If None, processes all clips for the video")


class CloudStorageRequest(BaseModel):
    """Request model for uploading clips to cloud storage and saving to database."""
    
    video_id: str = Field(..., description="Video ID to process clips for")
    clip_names: Optional[List[str]] = Field(default=None, description="Specific clip names to process. If None, processes all clips for the video")
    upload_to_cloud_bucket: bool = Field(default=True, description="Whether to upload clips to Google Cloud Storage")
    add_to_transcription_service: bool = Field(default=True, description="Whether to save clips data to database")
    transcriptions: Optional[Dict[str, Optional[str]]] = Field(default=None, description="Optional transcriptions to use instead of loading from file")


class ClipResult(BaseModel):
    """Result data for a single audio clip."""
    
    clip_name: str
    duration: float
    start_time: float
    end_time: float
    transcription: Optional[str] = None
    cloud_url: Optional[str] = None
    database_id: Optional[str] = None
    clip_path: Optional[str] = None  # Local file path
    audio_url: Optional[str] = None  # HTTP URL for frontend to access audio


class AudioProcessingResponse(BaseModel):
    """Response model for YouTube audio processing."""
    
    success: bool
    message: str
    video_metadata: Dict[str, Any]
    clips: List[ClipResult]
    total_clips: int


# New response schemas for separate processing steps

class AudioSplitResponse(BaseModel):
    """Response model for YouTube audio splitting."""
    
    success: bool
    message: str
    video_id: str
    video_metadata: Dict[str, Any]
    clips: List[Dict[str, Any]]  # Basic clip info without transcription/cloud data
    total_clips: int
    start_padding: float
    end_padding: float


class TranscribedClip(BaseModel):
    """Model for a transcribed audio clip."""
    
    clip_name: str
    transcription: Optional[str] = None  # Allow None for failed transcriptions


class TranscriptionResponse(BaseModel):
    """Response model for batch transcription."""
    
    success: bool
    message: str
    video_id: str
    transcribed_clips: List[TranscribedClip]  # List of transcribed clips
    total_transcribed: int
    failed_clips: List[str] = Field(default_factory=list)


class CloudStorageResponse(BaseModel):
    """Response model for cloud storage and database operations."""
    
    success: bool
    message: str
    video_id: str
    processed_clips: List[Dict[str, Any]]  # clip results with cloud_url and database_id
    total_processed: int
    failed_clips: List[str] = Field(default_factory=list)


class VideoExistenceResponse(BaseModel):
    """Response model for video existence check."""
    
    exists: bool
    video_details: Optional[Dict[str, Any]] = None
    audio_clips_count: int
    message: str


class VideoIdExtractionRequest(BaseModel):
    """Request model for extracting video ID from URL."""
    
    url: HttpUrl = Field(..., description="YouTube video URL to extract ID from")


class VideoIdExtractionResponse(BaseModel):
    """Response model for video ID extraction."""
    
    success: bool
    video_id: str
    url: str


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    version: str