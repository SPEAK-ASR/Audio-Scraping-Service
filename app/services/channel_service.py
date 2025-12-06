# app/services/channel_service.py
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.schemas.channel_schemas import ChannelCard


async def list_channels(db: AsyncSession) -> List[ChannelCard]:
    """
    Fetch all non-deleted channels ordered by created_at (desc)
    and map them to ChannelCard DTOs.
    """
    stmt = (
        select(Channel)
        .where(Channel.is_deleted.is_(False))
        .order_by(Channel.created_at.desc())
    )
    result = await db.execute(stmt)
    channels = result.scalars().all()

    return [
        ChannelCard(
            channelId=c.channel_id,
            channelTitle=c.channel_title,
            domain=c.domain,
            thumbnailUrl=c.thumbnail_url,
        )
        for c in channels
    ]


async def soft_delete_channel(db: AsyncSession, channel_id: str) -> bool:
    """
    Soft delete a channel by setting is_deleted = TRUE.
    Returns True if a row was updated, False if not found.
    """
    stmt = select(Channel).where(Channel.channel_id == channel_id)
    result = await db.execute(stmt)
    channel = result.scalar_one_or_none()

    if channel is None:
        return False

    channel.is_deleted = True
    await db.commit()
    return True
