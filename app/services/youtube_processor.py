"""
YouTube video processing service.

This service handles downloading YouTube videos, extracting audio,
and splitting into clips using Voice Activity Detection (VAD).
"""

import os
import json
import re
import contextlib
import collections
import wave
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yt_dlp
import webrtcvad
from app.utils import get_logger
from app.core.config import settings
from pydub import AudioSegment

# Filter
from df.enhance import enhance, init_df, load_audio, save_audio

logger = get_logger(__name__)


class Frame:
    """Represents a single audio frame for VAD processing."""
    
    def __init__(self, bytes_data, timestamp, duration):
        self.bytes = bytes_data
        self.timestamp = timestamp
        self.duration = duration


class YouTubeProcessor:
    """Service for processing YouTube videos into audio clips."""
    
    def __init__(self):
        self.temp_files = []
        self._check_dependencies()
        self.model, self.df_state, _ = init_df()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies (FFmpeg) are available."""
        if not shutil.which("ffmpeg"):
            logger.error("FFmpeg not found in PATH. Please install FFmpeg to use this service.")
            raise RuntimeError("FFmpeg is required but not found. Please install FFmpeg.")
        
        if not shutil.which("ffprobe"):
            logger.error("FFprobe not found in PATH. Please install FFmpeg to use this service.")
            raise RuntimeError("FFprobe is required but not found. Please install FFmpeg.")
        
        logger.info("FFmpeg dependencies verified successfully")
    
    def extract_video_id(self, youtube_url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    async def get_video_info(self, youtube_url: str) -> Tuple[Dict[str, Any], None]:
        """Get video metadata without downloading."""
        logger.info(f"Fetching video metadata from YouTube: {youtube_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                metadata = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'thumbnail': info.get('thumbnail'),
                    'url': youtube_url
                }
                
                logger.info(f"Successfully fetched metadata for video: {metadata.get('title', 'Unknown')}")
                return metadata, None
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube metadata fetch failed: {str(e)}")
            raise RuntimeError(f"YouTube metadata fetch failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during metadata fetch: {str(e)}")
            raise RuntimeError(f"Metadata fetch failed: {str(e)}")
    
    async def download_audio(self, youtube_url: str, output_file: str) -> Dict[str, Any]:
        """Download audio from YouTube video and extract metadata."""
        logger.info(f"Starting audio download from YouTube: {youtube_url}")
        
        # Get FFmpeg paths
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        
        # Download raw audio without post-processing first
        temp_raw_file = output_file.replace('.wav', '_raw.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_raw_file,
            'quiet': True,  # Reduce yt-dlp output noise
            'no_warnings': False,
        }
        
        try:
            # Get video metadata
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract metadata
                logger.info("Extracting video metadata")
                info = ydl.extract_info(youtube_url, download=False)
                metadata = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'thumbnail': info.get('thumbnail'),
                    'url': youtube_url
                }
                
                logger.info(f"Starting download for video: {metadata.get('title', 'Unknown')}")
                # Download raw audio file
                ydl.download([youtube_url])
                logger.info("Raw audio download completed successfully")
        
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube download failed: {str(e)}")
            raise RuntimeError(f"YouTube download failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during YouTube download: {str(e)}")
            raise
        
        # Find the downloaded raw audio file
        base_name = temp_raw_file.replace('.%(ext)s', '')
        actual_input_file = None
        
        # Common audio extensions that yt-dlp might download
        possible_extensions = ['.webm', '.m4a', '.mp3', '.ogg', '.opus', '.aac']
        for ext in possible_extensions:
            test_file = base_name + ext
            if os.path.exists(test_file):
                actual_input_file = test_file
                break
        
        if not actual_input_file:
            # List all files with the base name
            import glob
            matching_files = glob.glob(base_name + '*')
            if matching_files:
                actual_input_file = matching_files[0]
                logger.info(f"Found downloaded file: {actual_input_file}")
            else:
                raise FileNotFoundError(f"Downloaded audio file not found. Expected pattern: {base_name}*")
        
        try:
            logger.info(f"Converting {actual_input_file} to mono 16kHz WAV format")
            result = subprocess.run([
                "ffmpeg", "-y", "-i", actual_input_file,
                "-ac", "1", "-ar", "48000", "-acodec", "pcm_s16le", 
                output_file
            ], check=True, capture_output=True, text=True)
            logger.info("Audio conversion completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr}")
            raise RuntimeError(f"Audio conversion failed: {e.stderr}")
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg.")
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        
        # Clean up raw file
        if os.path.exists(actual_input_file):
            os.remove(actual_input_file)
            logger.info("Cleaned up temporary raw audio file")
        
        return metadata
    
    def frame_generator(self, frame_duration_ms: int, audio: bytes, sample_rate: int):
        """Generate audio frames for VAD processing."""
        n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
        offset = 0
        timestamp = 0.0
        duration = (float(n) / sample_rate) / 2.0
        
        while offset + n <= len(audio):
            yield Frame(audio[offset:offset + n], timestamp, duration)
            timestamp += duration
            offset += n
    
    def vad_collector(self, sample_rate: int, frame_duration_ms: int, 
                     padding_duration_ms: int, vad: webrtcvad.Vad, frames) -> List[Tuple[float, float]]:
        """Collect voice activity segments from audio frames."""
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False
        voiced_frames = []
        segments = []
        
        for frame in frames:
            is_speech = vad.is_speech(frame.bytes, sample_rate)
            
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    segment_start = voiced_frames[0].timestamp
                    segment_end = voiced_frames[-1].timestamp + voiced_frames[-1].duration
                    segments.append((segment_start, segment_end))
                    ring_buffer.clear()
                    voiced_frames = []
        
        if voiced_frames:
            segment_start = voiced_frames[0].timestamp
            segment_end = voiced_frames[-1].timestamp + voiced_frames[-1].duration
            segments.append((segment_start, segment_end))
        
        return segments
    
    def split_with_vad(self, input_file: str, output_dir: Path, video_id: str,
                      aggressiveness: int = 2, start_padding: float = 1.0, 
                      end_padding: float = 0.5) -> List[Dict[str, Any]]:
        """Split audio file using Voice Activity Detection."""
        with contextlib.closing(wave.open(input_file, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000, 48000)
            pcm_data = wf.readframes(wf.getnframes())
        
        vad = webrtcvad.Vad(aggressiveness)
        frames = list(self.frame_generator(30, pcm_data, sample_rate))
        segments = self.vad_collector(sample_rate, 30, 300, vad, frames)
        
        # Create output directory with base directory structure
        clips_output_dir = output_dir / "output" / video_id
        clips_output_dir.mkdir(parents=True, exist_ok=True)
        
        clips_data = []
        clip_counter = 1
        
        logger.info(f"Found {len(segments)} voice segments in audio")
        
        for start, end in segments:
            duration = end - start
            logger.info(f"Processing segment {clip_counter}: {start:.2f}s - {end:.2f}s (duration: {duration:.2f}s)")
            
            # Filter based on configured duration constraints
            if duration < settings.MIN_CLIP_DURATION or duration > settings.MAX_CLIP_DURATION:
                logger.info(f"Skipping segment {clip_counter}: duration {duration:.2f}s outside {settings.MIN_CLIP_DURATION}s-{settings.MAX_CLIP_DURATION}s range")
                continue
            
            clip_name = f"{video_id}-{clip_counter:03d}.wav"
            
            # Extract original audio segment
            with contextlib.closing(wave.open(input_file, 'rb')) as wf:
                wf.setpos(int(start * sample_rate))
                frames_to_read = int(duration * sample_rate)
                audio_data = wf.readframes(frames_to_read)
            
            # Add padding
            start_padding_frames = int(start_padding * sample_rate)
            end_padding_frames = int(end_padding * sample_rate)
            start_silence_bytes = b'\x00' * (start_padding_frames * sample_width)
            end_silence_bytes = b'\x00' * (end_padding_frames * sample_width)
            
            padded_data = start_silence_bytes + audio_data + end_silence_bytes
            padded_duration = duration + start_padding + end_padding
            
            # Save clip
            clip_path = clips_output_dir / clip_name
            with wave.open(str(clip_path), 'wb') as out_f:
                out_f.setnchannels(1)
                out_f.setsampwidth(2)
                out_f.setframerate(sample_rate)
                out_f.writeframes(padded_data)
            
            clips_data.append({
                'clip_name': clip_name,
                'start_time': round(start, 2),
                'end_time': round(end, 2),
                'duration': round(duration, 2),
                'padded_duration': round(padded_duration, 2)
            })
            
            clip_counter += 1
        
        logger.info(f"Successfully created {len(clips_data)} audio clips from {len(segments)} segments")
        return clips_data
    
    async def process_video(self, url: str, output_dir: Path, 
                          vad_aggressiveness: int = 2, start_padding: float = 1.0, 
                          end_padding: float = 0.5) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Process a YouTube video: download and split into clips."""
        video_id = self.extract_video_id(url)
        
        # Create temporary file for downloaded audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_audio_path = temp_file.name
            try:
                # Download audio
                metadata = await self.download_audio(url, temp_audio_path)

                # Enhance audio with DeepFilterNet (chunked for memory efficiency)
                logger.info("Starting audio enhancement with DeepFilterNet")
                self.enhance_audio_chunked(temp_audio_path, temp_audio_path, chunk_duration_seconds=600)
                logger.info("Audio enhancement completed successfully")

                # Re-sample audio to 16kHz
                self.convert_audio_to_sample_rate(
                    input_audio_path=temp_audio_path,
                    output_audio_path=temp_audio_path,
                    target_sample_rate=16000
                )
                
                # Split with VAD
                clips_data = self.split_with_vad(
                    input_file=temp_audio_path,
                    output_dir=output_dir,
                    video_id=video_id,
                    aggressiveness=vad_aggressiveness,
                    start_padding=start_padding,
                    end_padding=end_padding
                )
                
                return metadata, clips_data
            
            finally:
                # Clean up temporary file
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
    
    async def process_video_with_database(
        self, 
        url: str, 
        output_dir: Path,
        db_session,  # AsyncSession
        check_existing: bool = True,
        vad_aggressiveness: int = 2, 
        start_padding: float = 1.0, 
        end_padding: float = 0.5
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
        """
        Process a YouTube video with database integration.
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save clips
            db_session: Database session
            check_existing: Whether to check if video already exists
            vad_aggressiveness: VAD aggressiveness level
            start_padding: Start padding in seconds
            end_padding: End padding in seconds
            
        Returns:
            Tuple of (metadata, clips_data, is_new_video)
        """
        from app.services.database_service import DatabaseService
        
        video_id = self.extract_video_id(url)
        is_new_video = True
        
        # Check if video already exists in database
        if check_existing:
            existing_video = await DatabaseService.check_video_exists(db_session, video_id)
            if existing_video:
                logger.info(f"Video {video_id} already exists in database")
                is_new_video = False
                
                # Return existing video metadata
                existing_metadata = {
                    'video_id': existing_video.video_id,
                    'title': existing_video.title,
                    'description': existing_video.description,
                    'duration': existing_video.duration,
                    'uploader': existing_video.uploader,
                    'upload_date': existing_video.upload_date.strftime('%Y%m%d') if existing_video.upload_date else None,
                    'thumbnail': existing_video.thumbnail,
                    'url': existing_video.url
                }
                
                # Get existing clips
                existing_clips = await DatabaseService.get_video_audio_clips(db_session, video_id)
                clips_data = []
                for audio_clip in existing_clips:
                    clips_data.append({
                        'clip_name': audio_clip.audio_filename,
                        'clip_path': str(output_dir / "output" / video_id / audio_clip.audio_filename),
                        'start_time': self._time_to_seconds(audio_clip.start_time) if audio_clip.start_time else 0,
                        'end_time': self._time_to_seconds(audio_clip.end_time) if audio_clip.end_time else 0,
                        'duration': (self._time_to_seconds(audio_clip.end_time) - self._time_to_seconds(audio_clip.start_time)) if audio_clip.start_time and audio_clip.end_time else 0,
                        'padded_duration': audio_clip.padded_duration
                    })
                
                return existing_metadata, clips_data, is_new_video
        
        # Process new video
        metadata, clips_data = await self.process_video(
            url=url,
            output_dir=output_dir,
            vad_aggressiveness=vad_aggressiveness,
            start_padding=start_padding,
            end_padding=end_padding
        )
        
        return metadata, clips_data, is_new_video
    
    def _time_to_seconds(self, time_obj) -> float:
        """Convert time object to seconds."""
        if not time_obj:
            return 0.0
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000

    def enhance_audio_chunked(self, input_path: str, output_path: str, chunk_duration_seconds: int = 600):
        """
        Enhance audio using DeepFilterNet in chunks to handle long audio files.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save enhanced audio
            chunk_duration_seconds: Duration of each chunk in seconds (default: 600s)
        """
        import torch
        import numpy as np
        logger.info(f"Enhancing audio with DeepFilterNet (chunked processing)")
        
        # Load full audio
        audio, audio_meta = load_audio(input_path, sr=self.df_state.sr())
        sr = self.df_state.sr()  # Use the model's sample rate
        logger.info(f"Audio loaded: {audio.shape[1]} samples, {audio.shape[1]/sr:.2f} seconds")
        
        # Calculate chunk size in samples
        chunk_size = int(chunk_duration_seconds * sr)
        total_samples = audio.shape[1]
        
        # Process in chunks
        enhanced_chunks = []
        num_chunks = (total_samples + chunk_size - 1) // chunk_size  # Ceiling division
        
        logger.info(f"Processing audio in {num_chunks} chunks of {chunk_duration_seconds}s each")
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, total_samples)
            
            # Extract chunk
            chunk = audio[:, start_idx:end_idx]
            
            logger.info(f"Enhancing chunk {i+1}/{num_chunks} ({start_idx/sr:.1f}s - {end_idx/sr:.1f}s)")
            
            try:
                # Enhance chunk
                enhanced_chunk = enhance(self.model, self.df_state, chunk)
                enhanced_chunks.append(enhanced_chunk)
                
                # Clear GPU cache if using CUDA
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                logger.error(f"Error enhancing chunk {i+1}: {str(e)}")
                # Use original chunk if enhancement fails
                enhanced_chunks.append(chunk)
        
        # Concatenate all enhanced chunks
        logger.info("Concatenating enhanced chunks")
        enhanced_audio = torch.cat(enhanced_chunks, dim=1)
        
        # Save enhanced audio
        logger.info(f"Saving enhanced audio to {output_path}")
        save_audio(output_path, enhanced_audio, sr)
        logger.info("Audio enhancement completed successfully")

    def convert_audio_to_sample_rate(self, input_audio_path: str, output_audio_path: str, target_sample_rate: int = 16000) -> None:
        """Convert audio file to target sample rate."""
        # Ensure output directory exists
        output_dir = os.path.dirname(output_audio_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Load and convert audio
        audio = AudioSegment.from_file(input_audio_path)
        audio = audio.set_frame_rate(target_sample_rate)
        audio.export(output_audio_path, format="wav")
        
        logger.info(f"Audio converted to {target_sample_rate} Hz: {output_audio_path}")