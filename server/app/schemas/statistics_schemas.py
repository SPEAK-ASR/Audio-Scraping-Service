"""
Pydantic schemas for statistics API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date as date_type


class CategoryDurationData(BaseModel):
    """Duration statistics by category/domain."""
    category: str = Field(..., description="Category/domain name")
    total_duration_hours: float = Field(..., description="Total audio duration in hours")
    total_duration_minutes: float = Field(..., description="Total audio duration in minutes")
    clip_count: int = Field(..., description="Number of audio clips")
    video_count: int = Field(..., description="Number of videos")


class TranscriptionStatusData(BaseModel):
    """Transcription status statistics."""
    transcribed_count: int = Field(..., description="Number of transcribed audios")
    non_transcribed_count: int = Field(..., description="Number of non-transcribed audios")
    transcribed_duration_hours: float = Field(..., description="Duration of transcribed audios in hours")
    non_transcribed_duration_hours: float = Field(..., description="Duration of non-transcribed audios in hours")
    total_count: int = Field(..., description="Total number of audios")
    transcription_rate: float = Field(..., description="Percentage of transcribed audios")


class DailyTranscriptionData(BaseModel):
    """Daily transcription statistics."""
    date: date_type = Field(..., description="Date")
    transcription_count: int = Field(..., description="Number of transcriptions created")
    audio_count: int = Field(..., description="Number of audios processed")
    total_duration_hours: float = Field(..., description="Total duration in hours")


class AdminContributionData(BaseModel):
    """Admin contribution statistics."""
    admin: str = Field(..., description="Admin identifier")
    transcription_count: int = Field(..., description="Number of transcriptions")
    total_duration_hours: float = Field(..., description="Total duration transcribed in hours")
    percentage: float = Field(..., description="Percentage of total contributions")


class AudioDurationDistribution(BaseModel):
    """Audio duration distribution statistics."""
    range: str = Field(..., description="Duration range (e.g., '0-5s', '5-10s')")
    count: int = Field(..., description="Number of audio clips in this range")
    total_duration_hours: float = Field(..., description="Total duration in hours for this range")
    percentage: float = Field(..., description="Percentage of total clips")


class TotalDataSummary(BaseModel):
    """Overall data summary."""
    total_videos: int = Field(..., description="Total number of videos")
    total_audio_clips: int = Field(..., description="Total number of audio clips")
    total_duration_hours: float = Field(..., description="Total duration of all audios in hours")
    transcribed_duration_hours: float = Field(..., description="Total duration of transcribed audios in hours")
    total_transcriptions: int = Field(..., description="Total number of human transcriptions")
    average_clip_duration_seconds: float = Field(..., description="Average clip duration in seconds")


class SpeakerGenderData(BaseModel):
    """Speaker gender distribution."""
    gender: str = Field(..., description="Gender category")
    count: int = Field(..., description="Number of transcriptions")


class AudioSuitabilityData(BaseModel):
    """Audio suitability statistics."""
    suitable: int = Field(..., description="Number of suitable audios")
    unsuitable: int = Field(..., description="Number of unsuitable audios")
    unknown: int = Field(..., description="Number with unknown suitability")


class NoiseData(BaseModel):
    """Noise statistics."""
    with_noise: int = Field(..., description="Number of audios with noise")
    without_noise: int = Field(..., description="Number of audios without noise")
    unknown: int = Field(..., description="Number with unknown noise status")


class CodeMixingData(BaseModel):
    """Code mixing statistics."""
    code_mixed: int = Field(..., description="Number of code-mixed transcriptions")
    not_mixed: int = Field(..., description="Number of non-code-mixed transcriptions")
    unknown: int = Field(..., description="Number with unknown code-mixing status")


class SpeakerOverlappingData(BaseModel):
    """Speaker overlapping statistics."""
    with_overlap: int = Field(..., description="Number with speaker overlapping")
    without_overlap: int = Field(..., description="Number without speaker overlapping")
    unknown: int = Field(..., description="Number with unknown overlapping status")


class TranscriptionMetadata(BaseModel):
    """Transcription metadata statistics."""
    total_transcriptions: int = Field(..., description="Total transcriptions")
    audio_suitability: AudioSuitabilityData
    speaker_gender: List[SpeakerGenderData]
    noise: NoiseData
    code_mixing: CodeMixingData
    speaker_overlapping: SpeakerOverlappingData


class StatisticsResponse(BaseModel):
    """Complete statistics response."""
    success: bool = Field(default=True)
    message: str = Field(default="Statistics retrieved successfully")
    summary: TotalDataSummary
    category_durations: List[CategoryDurationData]
    transcription_status: TranscriptionStatusData
    daily_transcriptions: List[DailyTranscriptionData]
    admin_contributions: List[AdminContributionData]
    audio_distribution: List[AudioDurationDistribution]
    transcription_metadata: TranscriptionMetadata
