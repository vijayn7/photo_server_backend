"""
Photo manager utility module for the photo server backend.
Handles all operations related to photos including:
- Saving uploaded photos
- Retrieving photo information
- Managing photo metadata
"""

import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

# Default configuration
UPLOADS_DIR = "uploads"
METADATA_FILE = os.path.join(UPLOADS_DIR, "metadata.json")

def ensure_upload_dir():
    """
    Ensures that the uploads directory exists
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w") as f:
            json.dump({}, f)

def load_metadata() -> Dict[str, Any]:
    """
    Load the photo metadata from the JSON file
    
    Returns:
        dict: Dictionary with photo metadata
    """
    ensure_upload_dir()
    try:
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty dict if file doesn't exist or is invalid
        return {}

def save_metadata(metadata: Dict[str, Any]):
    """
    Save the photo metadata to the JSON file
    
    Args:
        metadata (dict): Dictionary with photo metadata
    """
    ensure_upload_dir()
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

def save_uploaded_file(file_obj, filename: str, username: str) -> Dict[str, Any]:
    """
    Save an uploaded file and update metadata
    
    Args:
        file_obj: The file object from FastAPI
        filename (str): The filename to save
        username (str): The username of the uploader
        
    Returns:
        dict: Metadata for the saved file
    """
    ensure_upload_dir()
    
    # Generate a unique filename if needed
    if os.path.exists(os.path.join(UPLOADS_DIR, filename)):
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
    
    # Save the file with proper error handling
    file_path = os.path.join(UPLOADS_DIR, filename)
    try:
        # Print some debug info
        print(f"Starting upload of file: {filename} by user: {username}")
        
        # Larger chunk size for better performance with large files
        chunk_size = 4 * 1024 * 1024  # 4MB chunks for better handling of large files
        bytes_written = 0
        with open(file_path, "wb") as buffer:
            # Read and write in chunks to handle large files better
            while chunk := file_obj.read(chunk_size):
                buffer.write(chunk)
                bytes_written += len(chunk)
                
                # Log progress for very large files
                if bytes_written % (100 * 1024 * 1024) == 0:  # Log every 100MB
                    print(f"Upload progress for {filename}: {bytes_written / (1024 * 1024):.1f}MB written")
        
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"Upload complete. File size: {file_size} bytes")
        
    except Exception as e:
        # If something goes wrong, clean up partial file and re-raise
        print(f"Error during file upload: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    
    # Update metadata
    metadata = load_metadata()
    file_metadata = {
        "filename": filename,
        "original_name": filename,
        "uploaded_by": username,
        "upload_date": datetime.now().isoformat(),
        "file_size": file_size,
        "file_type": os.path.splitext(filename)[1].lower()[1:],  # Extension without dot
    }
    
    metadata[filename] = file_metadata
    save_metadata(metadata)
    
    return file_metadata

def get_all_files(username: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all files with metadata
    
    Args:
        username (str, optional): If provided, filter by username
        
    Returns:
        list: List of dictionaries with file metadata
    """
    metadata = load_metadata()
    
    # Check for files that exist on disk but not in metadata
    actual_files = set(os.listdir(UPLOADS_DIR))
    # Remove metadata.json from the list
    if "metadata.json" in actual_files:
        actual_files.remove("metadata.json")
    
    metadata_files = set(metadata.keys())
    
    # Add missing files to metadata
    for filename in actual_files - metadata_files:
        file_path = os.path.join(UPLOADS_DIR, filename)
        if os.path.isfile(file_path):
            metadata[filename] = {
                "filename": filename,
                "original_name": filename,
                "uploaded_by": "unknown",
                "upload_date": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "file_size": os.path.getsize(file_path),
                "file_type": os.path.splitext(filename)[1].lower()[1:],
            }
    
    # Remove metadata for files that no longer exist
    for filename in metadata_files - actual_files:
        metadata.pop(filename, None)
    
    # Save updated metadata
    save_metadata(metadata)
    
    # Filter by username if provided
    result = []
    for filename, info in metadata.items():
        if username is None or info.get("uploaded_by") == username:
            result.append(info)
    
    # Sort by upload date (newest first)
    result.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    
    return result

def delete_file(filename: str, username: Optional[str] = None) -> bool:
    """
    Delete a file and its metadata
    
    Args:
        filename (str): Filename to delete
        username (str, optional): If provided, only delete if uploader matches
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    metadata = load_metadata()
    
    # Check if file exists in metadata
    if filename not in metadata:
        return False
    
    # Check username if provided
    if username is not None and metadata[filename].get("uploaded_by") != username:
        return False
    
    # Delete the file
    file_path = os.path.join(UPLOADS_DIR, filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from metadata
        metadata.pop(filename, None)
        save_metadata(metadata)
        return True
    except Exception:
        return False

def get_file_info(filename: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific file
    
    Args:
        filename (str): Filename to get info for
        
    Returns:
        dict: File metadata or None if not found
    """
    metadata = load_metadata()
    return metadata.get(filename)

def is_image_file(filename: str) -> bool:
    """
    Check if a file is an image based on extension
    
    Args:
        filename (str): Filename to check
        
    Returns:
        bool: True if file is an image, False otherwise
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    _, ext = os.path.splitext(filename.lower())
    return ext in image_extensions

def is_video_file(filename: str) -> bool:
    """
    Check if a file is a video based on extension
    
    Args:
        filename (str): Filename to check
        
    Returns:
        bool: True if file is a video, False otherwise
    """
    video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv']
    _, ext = os.path.splitext(filename.lower())
    return ext in video_extensions
