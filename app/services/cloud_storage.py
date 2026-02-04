"""
Google Cloud Storage service for uploading audio files.

This service handles uploading audio clips to Google Cloud Storage
and returns public URLs for the uploaded files.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from google.cloud import storage

from app.core.config import settings
from app.core.gcp_auth import gcp_auth_manager
from app.utils import get_logger

logger = get_logger(__name__)

# Thread pool for concurrent uploads
_upload_executor = ThreadPoolExecutor(max_workers=10)


class CloudStorageService:
    """Service for uploading files to Google Cloud Storage."""
    
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.client = self._initialize_client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def _initialize_client(self) -> storage.Client:
        """Initialize Google Cloud Storage client using the centralized auth manager."""
        return gcp_auth_manager.get_storage_client()
    
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
                logger.info(f"Successfully deleted {blob_name} from cloud storage")
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