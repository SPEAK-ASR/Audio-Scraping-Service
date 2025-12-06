"""
Channel routes for YouTube channel management.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_database_session
from app.schemas.channel_schemas import ChannelCard
from app.services import channel_service
from app.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/channels", tags=["Channels"])


@router.get("", response_model=List[ChannelCard])
async def get_channels(
    db: AsyncSession = Depends(get_async_database_session),
) -> List[ChannelCard]:
    """
    Get all non-deleted YouTube channels for the admin UI.

    Returns:
        List of ChannelCard objects with channelTitle, domain and thumbnailUrl.
    """
    try:
        logger.info("Fetching channel list")

        channels = await channel_service.list_channels(db)

        logger.info(f"Successfully retrieved {len(channels)} channels")
        return channels

    except Exception as e:
        logger.error(f"Error fetching channels: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve channels: {str(e)}"
        )


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    db: AsyncSession = Depends(get_async_database_session),
) -> None:
    """
    Soft delete a channel by marking is_deleted = TRUE.

    Args:
        channel_id: YouTube channel ID to delete.
    """
    try:
        logger.info(f"Soft deleting channel: {channel_id}")

        ok = await channel_service.soft_delete_channel(db, channel_id)
        if not ok:
            logger.warning(f"Channel not found: {channel_id}")
            raise HTTPException(
                status_code=404,
                detail="Channel not found"
            )

        logger.info(f"Channel successfully deleted: {channel_id}")

    except HTTPException:
        # Let 404 (or any explicit HTTPException) bubble up as-is
        raise
    except Exception as e:
        logger.error(f"Error deleting channel {channel_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete channel: {str(e)}"
        )
