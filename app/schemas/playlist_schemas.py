"""
Pydantic schemas for Playlist API request/response models.
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class PlaylistRequest(BaseModel):
    """Request model for fetching YouTube playlist videos."""
    
    playlist_url: HttpUrl = Field(..., description="Full YouTube playlist URL")
    limit: Optional[int] = Field(None, description="Max number of videos to return. If omitted, return all.")


class PlaylistVideo(BaseModel):
    """Model for a single video in a playlist."""
    
    video_id: str
    url: str
    title: str
    duration: int
    thumbnail: Optional[str] = None


class PlaylistResponse(BaseModel):
    """Response model for playlist video fetch."""
    
    success: bool
    playlist_id: str
    playlist_title: str
    total_videos: int
    returned_videos: int
    videos: List[PlaylistVideo]
