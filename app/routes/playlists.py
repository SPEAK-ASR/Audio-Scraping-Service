"""
Playlist processing routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.playlist_schemas import PlaylistRequest, PlaylistResponse, PlaylistVideo
from app.routes.youtube import get_youtube_processor
from app.core.database import get_async_database_session
from app.services.database_service import DatabaseService
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Playlists"])

@router.post("/playlist-videos", response_model=PlaylistResponse)
async def get_playlist_videos(
    request: PlaylistRequest,
    db: AsyncSession = Depends(get_async_database_session)
):
    """
    Fetch all video URLs from a YouTube playlist.
    Filters out videos that already exist in the database.
    """
    processor = get_youtube_processor()
    try:
        playlist_info = await processor.get_playlist_info(
            str(request.playlist_url), 
            limit=request.limit
        )
        
        # Get all video IDs from the playlist
        video_ids = [v['video_id'] for v in playlist_info['videos']]
        
        # Check which videos already exist in database (single query)
        existing_video_ids = await DatabaseService.check_videos_exist_batch(db, video_ids)
        existing_video_ids_set = set(existing_video_ids)
        
        # Filter out videos that already exist in the database
        filtered_videos = [
            PlaylistVideo(
                video_id=v['video_id'],
                url=v['url'],
                title=v['title'],
                duration=v['duration'],
                thumbnail=v['thumbnail']
            )
            for v in playlist_info['videos']
            if v['video_id'] not in existing_video_ids_set
        ]
        
        logger.info(f"Found {len(existing_video_ids)} existing videos, returning {len(filtered_videos)} new videos")
        
        # Return filtered videos (if limit is higher than filtered count, just return what we have)
        return PlaylistResponse(
            success=True,
            playlist_id=playlist_info['playlist_id'] or "unknown",
            playlist_title=playlist_info['playlist_title'] or "Unknown Playlist",
            total_videos=playlist_info.get('total_videos', len(playlist_info['videos'])),
            returned_videos=len(filtered_videos),
            videos=filtered_videos
        )
        
    except RuntimeError as e:
        error_msg = str(e).lower()
        if "playlist does not exist" in error_msg or "private playlist" in error_msg or "not found" in error_msg:
             raise HTTPException(
                status_code=404, 
                detail={
                    "success": False,
                    "error": "PLAYLIST_NOT_FOUND",
                    "message": "The playlist could not be found or is private"
                }
            )
        elif "valid url" in error_msg or "unsupported url" in error_msg:
             raise HTTPException(
                status_code=400, 
                detail={
                    "success": False,
                    "error": "INVALID_PLAYLIST_URL",
                    "message": "The provided URL is not a valid YouTube playlist"
                }
            )
        else:
             # Default fallback for other runtime errors from yt-dlp
             logger.error(f"Playlist fetch error: {e}")
             raise HTTPException(
                status_code=400, # Assume bad request/url for most yt-dlp errors for now
                detail={
                    "success": False,
                    "error": "PLAYLIST_FETCH_ERROR",
                    "message": f"Failed to fetch playlist: {str(e)}"
                }
            )

    except Exception as e:
        logger.error(f"Unexpected error fetching playlist: {e}")
        raise HTTPException(
            status_code=500, 
            detail={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": f"An unexpected error occurred: {str(e)}"
            }
        )
