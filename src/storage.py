"""Storage abstraction for asset management."""

import os
from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image
from pathlib import Path

from src.utils import ensure_dir


class StorageBackend(ABC):
    """Abstract storage backend interface."""
    
    @abstractmethod
    def save(self, path: str, image: Image.Image) -> str:
        """Save image to storage and return path."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> Optional[Image.Image]:
        """Load image from storage."""
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists in storage."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage implementation."""
    
    def __init__(self, base_path: str):
        """Initialize local storage with base path."""
        self.base_path = Path(base_path)
        ensure_dir(str(self.base_path))
    
    def save(self, path: str, image: Image.Image) -> str:
        """Save image to local filesystem."""
        full_path = self.base_path / path
        ensure_dir(str(full_path.parent))
        image.save(str(full_path), format='PNG')
        return str(full_path)
    
    def load(self, path: str) -> Optional[Image.Image]:
        """Load image from local filesystem."""
        full_path = self.base_path / path
        if not full_path.exists():
            return None
        try:
            return Image.open(str(full_path))
        except Exception:
            return None
    
    def exists(self, path: str) -> bool:
        """Check if file exists in local filesystem."""
        full_path = self.base_path / path
        return full_path.exists()


class AzureBlobStorage(StorageBackend):
    """Azure Blob Storage implementation (documented, not implemented for POC)."""
    
    def __init__(self, connection_string: str, container_name: str):
        """Initialize Azure Blob Storage."""
        # Production implementation would use azure-storage-blob
        raise NotImplementedError("Azure Blob Storage not implemented in POC")
    
    def save(self, path: str, image: Image.Image) -> str:
        """Save image to Azure Blob Storage."""
        raise NotImplementedError
    
    def load(self, path: str) -> Optional[Image.Image]:
        """Load image from Azure Blob Storage."""
        raise NotImplementedError
    
    def exists(self, path: str) -> bool:
        """Check if blob exists in Azure Blob Storage."""
        raise NotImplementedError


class S3Storage(StorageBackend):
    """AWS S3 storage implementation (documented, not implemented for POC)."""
    
    def __init__(self, bucket: str, region: str):
        """Initialize S3 storage."""
        # Production implementation would use boto3
        raise NotImplementedError("S3 Storage not implemented in POC")
    
    def save(self, path: str, image: Image.Image) -> str:
        """Save image to S3."""
        raise NotImplementedError
    
    def load(self, path: str) -> Optional[Image.Image]:
        """Load image from S3."""
        raise NotImplementedError
    
    def exists(self, path: str) -> bool:
        """Check if object exists in S3."""
        raise NotImplementedError

