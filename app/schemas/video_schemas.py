"""
Pydantic schemas for video management API endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """Metadata for a single video."""
    
    video_id: str = Field(..., description="YouTube video ID")
    num_of_clips: int = Field(..., description="Number of audio clips for this video")
    domain: Optional[str] = Field(None, description="Video domain/category")
    title: Optional[str] = Field(None, description="Video title")
    url: Optional[str] = Field(None, description="YouTube video URL")
    uploader: Optional[str] = Field(None, description="Video uploader/channel name")
    duration: Optional[int] = Field(None, description="Video duration in seconds")


class LowClipVideosResponse(BaseModel):
    """Response model for GET endpoint that returns videos with low clip counts."""
    
    video_ids: List[str] = Field(..., description="List of video IDs matching criteria")
    total_count: int = Field(..., description="Total number of videos matching criteria")
    metadata: List[VideoMetadata] = Field(..., description="Detailed metadata for each video")


class DeleteVideosRequest(BaseModel):
    """Request model for DELETE endpoint to remove videos."""
    
    video_ids: List[str] = Field(..., description="List of YouTube video IDs to delete")


class DeletedVideoInfo(BaseModel):
    """Information about a deleted video."""
    
    video_id: str = Field(..., description="YouTube video ID")
    video_link: Optional[str] = Field(None, description="YouTube video URL")
    domain: Optional[str] = Field(None, description="Video domain/category")
    num_clips_deleted: int = Field(0, description="Number of audio clips deleted for this video")


class DeleteVideosResponse(BaseModel):
    """Response model for DELETE endpoint."""
    
    total_deleted: int = Field(..., description="Total number of videos successfully deleted")
    total_failed: int = Field(..., description="Total number of videos that failed to delete")
    deleted_videos: List[DeletedVideoInfo] = Field(..., description="Details of successfully deleted videos")
    failed_videos: Optional[List[dict]] = Field(None, description="Details of videos that failed to delete")
    total_clips_deleted: int = Field(0, description="Total number of audio clips deleted across all videos")
    total_cloud_files_deleted: int = Field(0, description="Total number of files deleted from cloud storage")
    total_cloud_files_failed: int = Field(0, description="Total number of cloud files that failed to delete")
