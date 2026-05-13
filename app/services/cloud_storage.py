"""
Google Cloud Storage service for uploading audio files.

This service handles uploading audio clips to Google Cloud Storage
and returns public URLs for the uploaded files.
"""

import os
import asyncio
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from google.cloud import storage
from pydub import AudioSegment
import google.auth.transport.requests

from app.core.config import settings
from app.core.gcp_auth import gcp_auth_manager
from app.utils import get_logger

logger = get_logger(__name__)

# Thread pool for concurrent uploads and downloads
# Keep these lower to avoid overwhelming the connection pool
_upload_executor = ThreadPoolExecutor(max_workers=8)
_download_executor = ThreadPoolExecutor(max_workers=8)


class CloudStorageService:
    """Service for uploading files to Google Cloud Storage."""
    
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.client = self._initialize_client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def _initialize_client(self) -> storage.Client:
        """Initialize Google Cloud Storage client using the centralized auth manager."""
        # Get client with custom configuration for better connection pooling
        client = gcp_auth_manager.get_storage_client()
        
        # Configure the underlying session for better connection management
        if hasattr(client, '_http'):
            # Increase connection pool size for concurrent operations
            from urllib3.util.retry import Retry
            import requests.adapters
            
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,
                pool_maxsize=10,
                max_retries=Retry(total=3, backoff_factor=0.3)
            )
            client._http.mount('https://', adapter)
        
        return client
    
    async def upload_audio_file(self, file_path: str, blob_name: str) -> str:
        """
        Upload an audio file to Google Cloud Storage.
        
        Args:
            file_path: Local path to the audio file
            blob_name: Name/path for the file in the bucket
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            # Create blob
            blob = self.bucket.blob(blob_name)
            
            # Set content type for audio files
            blob.content_type = 'audio/wav'
            
            # Upload file
            with open(file_path, 'rb') as audio_file:
                blob.upload_from_file(audio_file)
            
            # Return the blob URL (works with uniform bucket-level access)
            blob_url = f"gs://{self.bucket_name}/{blob_name}"
            logger.info(f"Successfully uploaded {file_path} to {blob_name}")
            
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to cloud storage: {str(e)}")
            raise
    
    def _upload_file_sync(self, file_path: str, blob_name: str) -> str:
        """
        Synchronous upload method for use in thread pool.
        
        Args:
            file_path: Local path to the audio file
            blob_name: Name/path for the file in the bucket
            
        Returns:
            Public URL of the uploaded file
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.content_type = 'audio/wav'
            
            with open(file_path, 'rb') as audio_file:
                blob.upload_from_file(audio_file)
            
            blob_url = f"gs://{self.bucket_name}/{blob_name}"
            logger.info(f"Successfully uploaded {file_path} to {blob_name}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to cloud storage: {str(e)}")
            raise
    
    async def upload_batch_concurrent(
        self, 
        files: List[Dict[str, str]], 
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """
        Upload multiple files concurrently in batches.
        
        Args:
            files: List of dicts with 'file_path' and 'blob_name' keys
            batch_size: Number of concurrent uploads per batch
            
        Returns:
            Dict with 'successful' (list of {blob_name, url}) and 'failed' (list of {blob_name, error})
        """
        successful = []
        failed = []
        
        # Process in batches
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            logger.info(f"Processing upload batch {i // batch_size + 1}, files {i + 1}-{min(i + batch_size, len(files))}")
            
            # Create async tasks for concurrent uploads within batch
            tasks = []
            for file_info in batch:
                file_path = file_info['file_path']
                blob_name = file_info['blob_name']
                
                # Run sync upload in thread pool
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(
                    _upload_executor,
                    self._upload_file_sync,
                    file_path,
                    blob_name
                )
                tasks.append((blob_name, task))
            
            # Wait for all uploads in this batch to complete
            for blob_name, task in tasks:
                try:
                    url = await task
                    successful.append({
                        'blob_name': blob_name,
                        'url': url
                    })
                except Exception as e:
                    logger.error(f"Batch upload failed for {blob_name}: {e}")
                    failed.append({
                        'blob_name': blob_name,
                        'error': str(e)
                    })
        
        logger.info(f"Batch upload complete: {len(successful)} successful, {len(failed)} failed")
        return {
            'successful': successful,
            'failed': failed
        }
    
    def delete_files_batch(self, blob_names: List[str]) -> Dict[str, Any]:
        """
        Delete multiple files from cloud storage.
        
        Args:
            blob_names: List of blob names to delete
            
        Returns:
            Dict with 'successful' and 'failed' lists
        """
        successful = []
        failed = []
        
        for blob_name in blob_names:
            try:
                blob = self.bucket.blob(blob_name)
                blob.delete()
                successful.append(blob_name)
                logger.debug(f"Successfully deleted {blob_name} from cloud storage")
            except Exception as e:
                logger.error(f"Failed to delete {blob_name}: {str(e)}")
                failed.append({'blob_name': blob_name, 'error': str(e)})
        
        return {'successful': successful, 'failed': failed}
    
    async def upload_multiple_files(self, file_paths: list, blob_prefix: str = "") -> list:
        """
        Upload multiple audio files to cloud storage.
        
        Args:
            file_paths: List of local file paths
            blob_prefix: Prefix for blob names (like a folder path)
            
        Returns:
            List of dictionaries with file info and URLs
        """
        results = []
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            blob_name = f"{blob_prefix}/{filename}" if blob_prefix else filename
            
            try:
                url = await self.upload_audio_file(file_path, blob_name)
                results.append({
                    'filename': filename,
                    'local_path': file_path,
                    'blob_name': blob_name,
                    'url': url,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'filename': filename,
                    'local_path': file_path,
                    'blob_name': blob_name,
                    'url': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from cloud storage.
        
        Args:
            blob_name: Name/path of the file in the bucket
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"Successfully deleted {blob_name} from cloud storage")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {blob_name}: {str(e)}")
            return False
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Check if a file exists in cloud storage.
        
        Args:
            blob_name: Name/path of the file in the bucket
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except Exception as e:
            logger.error(f"Error checking if {blob_name} exists: {str(e)}")
            return False
    
    def _get_audio_duration_sync(self, blob_name: str) -> Optional[float]:
        """
        Synchronous method to get audio duration for use in thread pool.
        
        Args:
            blob_name: Name/path of the audio file in the bucket
            
        Returns:
            Duration in seconds, or None if failed
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Check if file exists
            if not blob.exists():
                return None
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Download the blob
                blob.download_to_filename(temp_path)
                
                # Get duration using pydub
                audio = AudioSegment.from_file(temp_path)
                duration_seconds = len(audio) / 1000.0  # pydub returns milliseconds
                
                return duration_seconds
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Failed to get duration for {blob_name}: {str(e)}")
            return None
    
    async def get_audio_duration(self, blob_name: str) -> Optional[float]:
        """
        Get the duration of an audio file from cloud storage (async wrapper).
        
        Args:
            blob_name: Name/path of the audio file in the bucket
            
        Returns:
            Duration in seconds, or None if failed
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _download_executor,
            self._get_audio_duration_sync,
            blob_name
        )
    
    async def get_audio_durations_batch(self, blob_names: List[str], max_concurrent: int = 8) -> Dict[str, Optional[float]]:
        """
        Get durations for multiple audio files concurrently.
        
        Args:
            blob_names: List of blob names to check
            max_concurrent: Maximum number of concurrent operations (default 8 to match connection pool)
            
        Returns:
            Dictionary mapping blob_name to duration (or None if failed)
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def get_with_semaphore(blob_name: str):
            async with semaphore:
                duration = await self.get_audio_duration(blob_name)
                return blob_name, duration
        
        tasks = [get_with_semaphore(name) for name in blob_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        durations = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in batch duration check: {result}")
                continue
            blob_name, duration = result
            durations[blob_name] = duration
        
        return durations