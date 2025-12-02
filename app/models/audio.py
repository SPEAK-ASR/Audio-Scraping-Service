"""
SQLAlchemy model for Audio table.
"""

from sqlalchemy import Column, Integer, Text, DateTime, Time, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Audio(Base):
    """
    SQLAlchemy model for the Audio table.
    Stores audio clip data with foreign key reference to YouTube videos.
    """
    
    __tablename__ = "Audio"
    
    audio_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audio_filename = Column(Text, nullable=False, unique=True)
    google_transcription = Column(Text, nullable=False, default="")
    transcription_count = Column(Integer, nullable=False, default=0)
    leased_until = Column(DateTime(timezone=False), nullable=True)
    start_time = Column(Time(timezone=False), nullable=True)
    end_time = Column(Time(timezone=False), nullable=True)
    padded_duration = Column(Float, nullable=True)
    youtube_video_id = Column(UUID(as_uuid=True), ForeignKey("YouTube_Video.id"), nullable=True)
    
    # Relationship to YouTube video
    youtube_video = relationship("YouTubeVideo", back_populates="audio_clips")
    
    # Relationship to transcriptions
    transcriptions = relationship("Transcription", back_populates="audio")
    
    def __repr__(self):
        return f"<Audio(audio_id='{self.audio_id}', filename='{self.audio_filename}')>"