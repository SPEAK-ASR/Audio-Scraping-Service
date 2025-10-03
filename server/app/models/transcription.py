"""
SQLAlchemy model for Transcriptions table.
"""

from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Transcription(Base):
    """
    SQLAlchemy model for the Transcriptions table.
    Stores human transcriptions for audio clips.
    """
    
    __tablename__ = "Transcriptions"
    
    trans_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcription = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    has_noise = Column(Boolean, nullable=True)
    is_code_mixed = Column(Boolean, nullable=True)
    audio_id = Column(UUID(as_uuid=True), ForeignKey("Audio.audio_id"), nullable=False)
    is_speaker_overlappings_exist = Column(Boolean, nullable=True)
    speaker_gender = Column("speaker_gender", nullable=True)  # USER-DEFINED type
    is_audio_suitable = Column(Boolean, nullable=True, default=True)
    admin = Column("admin", nullable=True)  # USER-DEFINED type
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to audio
    audio = relationship("Audio", back_populates="transcriptions")
    
    def __repr__(self):
        return f"<Transcription(trans_id='{self.trans_id}', audio_id='{self.audio_id}')>"