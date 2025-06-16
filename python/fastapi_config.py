"""
FastAPI configuration for large file uploads
"""

from fastapi import FastAPI, UploadFile
from typing import Any, Dict, Optional, Union

class LargeFileUploadConfig:
    """
    Configuration for FastAPI to handle large file uploads
    """
    def __init__(self):
        self.max_upload_size: int = 10 * 1024 * 1024 * 1024  # 10GB
        
    def create_app(self) -> FastAPI:
        """
        Create FastAPI app with large upload configuration
        """
        app = FastAPI()
        return app
