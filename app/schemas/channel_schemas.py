# app/schemas/channel_schemas.py
from typing import List, Optional
from pydantic import BaseModel


class ChannelCard(BaseModel):
    """
    Response model for channel cards in the admin UI.
    """

    channelId: str
    channelTitle: Optional[str] = None
    domain: str
    thumbnailUrl: Optional[str] = None
