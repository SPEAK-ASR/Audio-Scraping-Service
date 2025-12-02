"""
SQLAlchemy model for YouTube_Video table.
"""

from sqlalchemy import Column, Text, BigInteger, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class YouTubeVideo(Base):
    """
    SQLAlchemy model for the YouTube_Video table.
    Stores metadata about processed YouTube videos.
    """
    
    __tablename__ = "YouTube_Video"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    video_id = Column(Text, nullable=False, unique=True)  # YouTube video ID
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(BigInteger, nullable=True)  # Duration in seconds
    uploader = Column(Text, nullable=True)
    upload_date = Column(Date, nullable=True)
    thumbnail = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    # Use existing PostgreSQL enum, pass string values directly
    domain = Column(ENUM(
        'education', 'health', 'politics_and_government', 'news_and_current_affairs',
        'science', 'technology_and_computing', 'business_and_finance', 'entertainment',
        'food_and_drink', 'law_and_justice', 'environment_and_sustainability',
        'religion', 'media_marketing', 'history_and_cultural', 'work_and_careers', 'others',
        name='domain_enum', create_type=False
    ), nullable=True)
    
    # Relationship to Audio clips
    audio_clips = relationship("Audio", back_populates="youtube_video")
    
    def __repr__(self):
        return f"<YouTubeVideo(id='{self.id}', video_id='{self.video_id}', title='{self.title}')>"