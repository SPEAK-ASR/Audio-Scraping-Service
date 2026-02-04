"""
Google Speech-to-Text transcription service.

This service handles audio transcription using Google Cloud Speech-to-Text API.
"""

import os
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from google.cloud import speech

from app.core.gcp_auth import gcp_auth_manager
from app.utils import get_logger

logger = get_logger(__name__)

# Thread pool for concurrent transcriptions
_transcription_executor = ThreadPoolExecutor(max_workers=5)


class TranscriptionService:
    """Service for transcribing audio files using Google Speech-to-Text."""
    
    def __init__(self):
        # Use the centralized auth manager to get credentials
        credentials = gcp_auth_manager.get_credentials()
        if credentials:
            self.client = speech.SpeechClient(credentials=credentials)
        else:
            # Fall back to default credentials
            self.client = speech.SpeechClient()
    
    
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe an audio file using Google Speech-to-Text.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_content = audio_file.read()
            
            # Configure audio and recognition settings
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="si",  # Sinhala language code
                enable_automatic_punctuation=True,
                # Removed model="latest_long" as it's not supported for Sinhala
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Collect transcriptions
            transcriptions = []
            for result in response.results:
                transcriptions.append(result.alternatives[0].transcript)
            
            # Join all transcriptions
            full_transcription = " ".join(transcriptions) if transcriptions else None
            
            if full_transcription:
                logger.info(f"Successfully transcribed audio: {os.path.basename(audio_file_path)}")
            else:
                logger.warning(f"No transcription found for: {os.path.basename(audio_file_path)}")
            
            return full_transcription
            
        except Exception as e:
            logger.error(f"Transcription failed for {audio_file_path}: {str(e)}")
            return None
    
    def _transcribe_audio_sync(self, audio_file_path: str) -> Optional[str]:
        """
        Synchronous transcription method for use in thread pool.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_content = audio_file.read()
            
            # Configure audio and recognition settings
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="si",  # Sinhala language code
                enable_automatic_punctuation=True,
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Collect transcriptions
            transcriptions = []
            for result in response.results:
                transcriptions.append(result.alternatives[0].transcript)
            
            # Join all transcriptions
            full_transcription = " ".join(transcriptions) if transcriptions else None
            
            if full_transcription:
                logger.info(f"Successfully transcribed audio: {os.path.basename(audio_file_path)}")
            else:
                logger.warning(f"No transcription found for: {os.path.basename(audio_file_path)}")
            
            return full_transcription
            
        except Exception as e:
            logger.error(f"Transcription failed for {audio_file_path}: {str(e)}")
            return None
    
    async def transcribe_batch_concurrent(
        self, 
        audio_files: List[str], 
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """
        Transcribe multiple audio files concurrently in batches.
        
        Args:
            audio_files: List of audio file paths
            batch_size: Number of concurrent transcriptions per batch
            
        Returns:
            Dict with 'successful' (list of {filename, transcription}) and 'failed' (list of filenames)
        """
        successful = []
        failed = []
        
        # Process in batches
        for i in range(0, len(audio_files), batch_size):
            batch = audio_files[i:i + batch_size]
            logger.info(f"Processing transcription batch {i // batch_size + 1}, files {i + 1}-{min(i + batch_size, len(audio_files))}")
            
            # Create async tasks for concurrent transcriptions within batch
            tasks = []
            for audio_file in batch:
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(
                    _transcription_executor,
                    self._transcribe_audio_sync,
                    audio_file
                )
                tasks.append((audio_file, task))
            
            # Wait for all transcriptions in this batch to complete
            for audio_file, task in tasks:
                try:
                    transcription = await task
                    filename = os.path.basename(audio_file)
                    successful.append({
                        'filename': filename,
                        'filepath': audio_file,
                        'transcription': transcription
                    })
                except Exception as e:
                    filename = os.path.basename(audio_file)
                    logger.error(f"Batch transcription failed for {filename}: {e}")
                    failed.append(filename)
        
        logger.info(f"Batch transcription complete: {len(successful)} processed, {len(failed)} failed")
        return {
            'successful': successful,
            'failed': failed
        }
    
    async def transcribe_multiple_files(self, audio_files: List[str]) -> List[dict]:
        """
        Transcribe multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            List of dictionaries with filename and transcription
        """
        results = []
        
        for audio_file in audio_files:
            transcription = await self.transcribe_audio(audio_file)
            results.append({
                'filename': os.path.basename(audio_file),
                'filepath': audio_file,
                'transcription': transcription
            })
        
        return results