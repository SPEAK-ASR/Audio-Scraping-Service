"""
SQLAlchemy model for the channels table.
"""

from sqlalchemy import Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from app.core.database import Base


class Channel(Base):
    """
    SQLAlchemy model for the channels table.
    Stores YouTube channels and metadata used for audio scraping.
    """

    __tablename__ = "Channel"  # must match your DB table name

    channel_id = Column(Text, primary_key=True)
    topic_categories = Column(ARRAY(Text), nullable=False)
    domain = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self) -> str:
        return f"<Channel(channel_id='{self.channel_id}')>"
