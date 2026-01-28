"""
Playlist processing routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from app.schemas.playlist_schemas import PlaylistRequest, PlaylistResponse, PlaylistVideo
from app.routes.youtube import get_youtube_processor
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Playlists"])

@router.post("/playlist-videos", response_model=PlaylistResponse)
async def get_playlist_videos(request: PlaylistRequest):
    """
    Fetch all video URLs from a YouTube playlist.
    """
    processor = get_youtube_processor()
    try:
        playlist_info = await run_in_threadpool(
            processor.get_playlist_info,
            str(request.playlist_url), 
            limit=request.limit
        )
        
        # Convert dictionary videos to Pydantic models to ensure validation (though response_model handles it too)
        videos = [
            PlaylistVideo(
                video_id=v['video_id'],
                url=v['url'],
                title=v['title'],
                duration=v['duration'],
                thumbnail=v['thumbnail']
            ) for v in playlist_info['videos']
        ]

        return PlaylistResponse(
            success=True,
            playlist_id=playlist_info['playlist_id'] or "unknown",
            playlist_title=playlist_info['playlist_title'] or "Unknown Playlist",
            total_videos=playlist_info.get('total_videos', len(videos)),
            returned_videos=len(videos),
            videos=videos
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
