# app/schemas/channel.py
from typing import List, Optional
from pydantic import BaseModel


class ChannelCard(BaseModel):
    """
    Response model for channel cards in the admin UI.
    """

    channelId: str
    topicCategories: List[str]
    thumbnailUrl: Optional[str] = None
