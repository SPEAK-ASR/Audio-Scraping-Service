"""
Google Cloud Storage service for uploading audio files.

This service handles uploading audio clips to Google Cloud Storage
and returns public URLs for the uploaded files.
"""

import os
from typing import Optional
from pathlib import Path

from google.cloud import storage

from app.core.config import settings
from app.core.gcp_auth import gcp_auth_manager
from app.utils import get_logger

logger = get_logger(__name__)


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