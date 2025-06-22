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
from PIL import Image, ImageOps
import logging
import piexif
import exifread
try:
    import piexif
    import exifread
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False
    print("Warning: EXIF libraries not available. Install with: pip install piexif exifread")

# Default configuration - use environment variables or fallback to development paths
UPLOADS_DIR = os.environ.get("PHOTOS_PATH", os.path.join(os.getcwd(), "photos"))
GLOBAL_FOLDER = "global"
METADATA_FILE = os.path.join(UPLOADS_DIR, "metadata.json")
DEFAULT_THUMBNAIL_SIZE = 256  # Default thumbnail size in pixels

def extract_exif_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract EXIF metadata from an image file
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Dictionary containing EXIF metadata
    """
    metadata = {}
    
    try:
        # Try using piexif first
        import piexif
        
        with open(image_path, 'rb') as f:
            exif_dict = piexif.load(f.read())
        
        # Extract common EXIF data
        if "0th" in exif_dict:
            ifd = exif_dict["0th"]
            
            # Camera make and model
            if piexif.ImageIFD.Make in ifd:
                metadata["camera_make"] = ifd[piexif.ImageIFD.Make].decode('utf-8', errors='ignore')
            if piexif.ImageIFD.Model in ifd:
                metadata["camera_model"] = ifd[piexif.ImageIFD.Model].decode('utf-8', errors='ignore')
            
            # Image dimensions
            if piexif.ImageIFD.ImageWidth in ifd:
                metadata["width"] = ifd[piexif.ImageIFD.ImageWidth]
            if piexif.ImageIFD.ImageLength in ifd:
                metadata["height"] = ifd[piexif.ImageIFD.ImageLength]
            
            # Orientation
            if piexif.ImageIFD.Orientation in ifd:
                metadata["orientation"] = ifd[piexif.ImageIFD.Orientation]
        
        if "Exif" in exif_dict:
            exif_ifd = exif_dict["Exif"]
            
            # Date taken
            if piexif.ExifIFD.DateTimeOriginal in exif_ifd:
                date_str = exif_ifd[piexif.ExifIFD.DateTimeOriginal].decode('utf-8', errors='ignore')
                try:
                    metadata["date_taken"] = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").isoformat()
                except ValueError:
                    metadata["date_taken"] = date_str
            
            # ISO speed
            if piexif.ExifIFD.ISOSpeedRatings in exif_ifd:
                metadata["iso"] = exif_ifd[piexif.ExifIFD.ISOSpeedRatings]
            
            # Exposure time
            if piexif.ExifIFD.ExposureTime in exif_ifd:
                exposure = exif_ifd[piexif.ExifIFD.ExposureTime]
                metadata["exposure_time"] = f"{exposure[0]}/{exposure[1]}"
            
            # F-number (aperture)
            if piexif.ExifIFD.FNumber in exif_ifd:
                f_number = exif_ifd[piexif.ExifIFD.FNumber]
                metadata["f_number"] = f"{f_number[0]}/{f_number[1]}"
            
            # Focal length
            if piexif.ExifIFD.FocalLength in exif_ifd:
                focal = exif_ifd[piexif.ExifIFD.FocalLength]
                metadata["focal_length"] = f"{focal[0]}/{focal[1]}mm"
        
        # GPS data
        if "GPS" in exif_dict:
            gps_ifd = exif_dict["GPS"]
            if gps_ifd:
                metadata["has_gps"] = True
                # Extract GPS coordinates if needed (more complex parsing)
            else:
                metadata["has_gps"] = False
        else:
            metadata["has_gps"] = False
            
    except ImportError:
        # Fallback to exifread if piexif not available
        try:
            import exifread
            
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            # Extract basic information
            if 'Image Make' in tags:
                metadata["camera_make"] = str(tags['Image Make'])
            if 'Image Model' in tags:
                metadata["camera_model"] = str(tags['Image Model'])
            if 'EXIF DateTimeOriginal' in tags:
                metadata["date_taken"] = str(tags['EXIF DateTimeOriginal'])
            if 'EXIF ISOSpeedRatings' in tags:
                metadata["iso"] = str(tags['EXIF ISOSpeedRatings'])
            if 'EXIF ExposureTime' in tags:
                metadata["exposure_time"] = str(tags['EXIF ExposureTime'])
            if 'EXIF FNumber' in tags:
                metadata["f_number"] = str(tags['EXIF FNumber'])
            if 'EXIF FocalLength' in tags:
                metadata["focal_length"] = str(tags['EXIF FocalLength'])
            if 'Image ImageWidth' in tags:
                metadata["width"] = str(tags['Image ImageWidth'])
            if 'Image ImageLength' in tags:
                metadata["height"] = str(tags['Image ImageLength'])
                
        except ImportError:
            # No EXIF libraries available
            pass
    except Exception as e:
        # Log error but don't fail
        logging.warning(f"Failed to extract EXIF data from {image_path}: {str(e)}")
    
    # Fallback: get basic image dimensions using PIL
    if not metadata.get("width") or not metadata.get("height"):
        try:
            with Image.open(image_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["resolution"] = f"{img.width}x{img.height}"
        except Exception:
            pass
    else:
        metadata["resolution"] = f"{metadata.get('width', 0)}x{metadata.get('height', 0)}"
    
    return metadata

def format_file_size(size_bytes: int) -> str:
    """
    Format file size from bytes to human-readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Human-readable size (e.g., "5.2 MB")
    """
    # Define size units
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    
    # Calculate the appropriate unit
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    
    # Format the output with 2 decimal places for larger units, no decimals for bytes
    if i == 0:  # bytes
        return f"{int(size)} {units[i]}"
    else:
        return f"{size:.2f} {units[i]}"

def get_user_folder_path(username: str) -> str:
    """
    Get the folder path for a specific user
    
    Args:
        username (str): Username
        
    Returns:
        str: Path to user's folder
    """
    return os.path.join(UPLOADS_DIR, username)

def get_global_folder_path() -> str:
    """
    Get the path to the global shared folder
    
    Returns:
        str: Path to global folder
    """
    return os.path.join(UPLOADS_DIR, GLOBAL_FOLDER)

def ensure_user_folder(username: str):
    """
    Ensure that a user's folder exists
    
    Args:
        username (str): Username to create folder for
    """
    user_folder = get_user_folder_path(username)
    os.makedirs(user_folder, exist_ok=True)

def ensure_upload_dir():
    """
    Ensures that the uploads directory and global folder exist
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(get_global_folder_path(), exist_ok=True)
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
    ensure_user_folder(username)
    
    # Get user's folder path
    user_folder = get_user_folder_path(username)
    
    # Generate a unique filename if needed
    if os.path.exists(os.path.join(user_folder, filename)):
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
    
    # Save the file with proper error handling
    file_path = os.path.join(user_folder, filename)
    try:
        # Print some debug info
        print(f"Starting upload of file: {filename} by user: {username} to {user_folder}")
        
        # Larger chunk size for better performance with large files
        chunk_size = 4 * 1024 * 1024  # 4MB chunks for better handling of large files
        bytes_written = 0
        
        # Check if we can read from the file object (this will fail if file is closed or invalid)
        try:
            # Try to get current position to verify file object is valid
            current_pos = file_obj.tell()
        except Exception as e:
            print(f"Error accessing file object: {str(e)}")
            raise IOError(f"Invalid file object: {str(e)}") from e
        
        with open(file_path, "wb") as buffer:
            # Read and write in chunks to handle large files better
            try:
                while chunk := file_obj.read(chunk_size):
                    buffer.write(chunk)
                    bytes_written += len(chunk)
                    
                    # Log progress for very large files
                    if bytes_written % (100 * 1024 * 1024) == 0:  # Log every 100MB
                        print(f"Upload progress for {filename}: {bytes_written / (1024 * 1024):.1f}MB written")
            except Exception as chunk_error:
                print(f"Error during chunk read/write: {str(chunk_error)}")
                raise IOError(f"Upload failed during file transfer: {str(chunk_error)}") from chunk_error
                
        print(f"Upload complete for {filename}: Total size {bytes_written / (1024 * 1024):.2f} MB")
        
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"Upload complete. File size: {file_size} bytes")
        
    except Exception as e:
        # If something goes wrong, clean up partial file and re-raise
        print(f"Error during file upload: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed partial file: {file_path}")
        
        # Add more diagnostic information to the error
        error_details = str(e)
        if hasattr(file_obj, 'file'):
            error_details += f" (File object type: {type(file_obj).__name__}, File attribute type: {type(file_obj.file).__name__})"
        
        raise IOError(f"File upload failed: {error_details}") from e
    
    # Update metadata with folder info
    metadata = load_metadata()
    file_metadata = {
        "filename": filename,
        "original_name": filename,
        "uploaded_by": username,
        "upload_date": datetime.now().isoformat(),
        "upload_time": datetime.now().isoformat(),  # Alias for compatibility
        "file_size": file_size,
        "size": format_file_size(file_size),
        "file_type": os.path.splitext(filename)[1].lower()[1:],
        "folder": username,  # Track which folder the file is in
        "file_path": os.path.join(username, filename),  # Relative path from photos root
        "is_favorite": False,  # Default to not favorite
        "metadata": {}  # Initialize metadata field
    }
    
    # Extract EXIF metadata for images
    if is_image(filename):
        try:
            exif_metadata = extract_exif_metadata(file_path)
            file_metadata["metadata"] = exif_metadata
            print(f"Extracted EXIF metadata for {filename}: {len(exif_metadata)} fields")
        except Exception as exif_error:
            print(f"Error extracting EXIF metadata for {filename}: {str(exif_error)}")
            file_metadata["metadata"] = {}
    
    # Use a unique key that includes the folder to avoid conflicts
    unique_key = f"{username}/{filename}"
    metadata[unique_key] = file_metadata
    save_metadata(metadata)
    
    # Generate thumbnail if it's an image
    if is_image(filename):
        try:
            thumbnail_path = generate_thumbnail(username, file_path)
            if thumbnail_path:
                print(f"Successfully generated thumbnail for {filename}")
                file_metadata["has_thumbnail"] = True
                file_metadata["thumbnail_path"] = f"/thumbnails/{filename}"
            else:
                print(f"Failed to generate thumbnail for {filename}")
                file_metadata["has_thumbnail"] = False
        except Exception as thumb_error:
            print(f"Error generating thumbnail for {filename}: {str(thumb_error)}")
            file_metadata["has_thumbnail"] = False
    else:
        file_metadata["has_thumbnail"] = False
    
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
    metadata_updated = False
    
    # Scan all user folders and global folder for files
    ensure_upload_dir()
    
    # Get all directories in the uploads folder (user folders + global)
    try:
        all_items = os.listdir(UPLOADS_DIR)
        user_folders = [item for item in all_items if os.path.isdir(os.path.join(UPLOADS_DIR, item)) and item != "lost+found"]
    except OSError:
        user_folders = []
    
    # Track all actual files with their folder paths
    actual_files = set()
    for folder in user_folders:
        folder_path = os.path.join(UPLOADS_DIR, folder)
        try:
            files_in_folder = os.listdir(folder_path)
            for file in files_in_folder:
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    # Use folder/filename as unique key
                    unique_key = f"{folder}/{file}"
                    actual_files.add(unique_key)
        except OSError:
            continue
    
    metadata_files = set(metadata.keys())
    
    # Add missing files to metadata
    for unique_key in actual_files - metadata_files:
        folder, filename = unique_key.split("/", 1)
        file_path = os.path.join(UPLOADS_DIR, folder, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            metadata[unique_key] = {
                "filename": filename,
                "original_name": filename,
                "uploaded_by": folder if folder != GLOBAL_FOLDER else "unknown",
                "upload_date": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "file_size": file_size,
                "size": format_file_size(file_size),
                "file_type": os.path.splitext(filename)[1].lower()[1:],
                "folder": folder,
                "file_path": unique_key
            }
            metadata_updated = True
    
    # Update existing metadata entries to add missing attributes
    for unique_key in metadata_files.intersection(actual_files):
        file_metadata = metadata[unique_key]
        updated = False
        
        # Add size attribute if missing
        if "size" not in file_metadata and "file_size" in file_metadata:
            file_metadata["size"] = format_file_size(file_metadata["file_size"])
            updated = True
        
        # Add folder and file_path if missing (for backward compatibility)
        if "folder" not in file_metadata or "file_path" not in file_metadata:
            if "/" in unique_key:
                folder, filename = unique_key.split("/", 1)
                file_metadata["folder"] = folder
                file_metadata["file_path"] = unique_key
                updated = True
        
        if updated:
            metadata_updated = True
    
    # Remove metadata for files that no longer exist
    for unique_key in metadata_files - actual_files:
        metadata.pop(unique_key, None)
        metadata_updated = True
    
    # Save updated metadata
    if metadata_updated:
        save_metadata(metadata)
    
    # Filter by username if provided
    result = []
    for unique_key, info in metadata.items():
        # If username filter is provided, only include files from that user's folder
        if username is None or info.get("uploaded_by") == username or info.get("folder") == username:
            result.append(info)
    
    # Sort by upload date (newest first)
    result.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    
    return result

def delete_file(filename: str, username: Optional[str] = None, is_admin: bool = False) -> bool:
    """
    Delete a file and its metadata
    
    Args:
        filename (str): Filename or unique key (folder/filename) to delete
        username (str, optional): If provided, only delete if uploader matches
        is_admin (bool, optional): If True, allow deletion regardless of uploader
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    metadata = load_metadata()
    
    # Handle both old format (just filename) and new format (folder/filename)
    unique_key = filename
    if "/" not in filename and username:
        # If no folder specified, assume it's in the user's folder
        unique_key = f"{username}/{filename}"
    
    # Check if file exists in metadata
    if unique_key not in metadata:
        # Try to find the file in any folder if admin
        if is_admin:
            for key in metadata.keys():
                if key.endswith(f"/{filename}"):
                    unique_key = key
                    break
            else:
                return False
        else:
            return False
    
    file_info = metadata[unique_key]
    
    # Check username if provided and user is not an admin
    if not is_admin and username is not None:
        if file_info.get("uploaded_by") != username and file_info.get("folder") != username:
            return False
    
    # Get the actual file path
    if "file_path" in file_info:
        file_path = os.path.join(UPLOADS_DIR, file_info["file_path"])
    else:
        # Fallback for old metadata format
        file_path = os.path.join(UPLOADS_DIR, unique_key)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Also delete the thumbnail if it exists
        # Extract username from unique_key or file_info
        file_username = file_info.get("uploaded_by") or file_info.get("folder")
        if file_username and is_image(filename):
            delete_thumbnail(file_username, filename)
        
        # Remove from metadata
        metadata.pop(unique_key, None)
        save_metadata(metadata)
        return True
    except Exception:
        return False

def get_file_info(filename: str, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific file
    
    Args:
        filename (str): Filename or unique key (folder/filename) to get info for
        username (str, optional): Username to help locate the file
        
    Returns:
        dict: File metadata or None if not found
    """
    metadata = load_metadata()
    
    # Handle both old format (just filename) and new format (folder/filename)
    unique_key = filename
    if "/" not in filename and username:
        # If no folder specified, assume it's in the user's folder
        unique_key = f"{username}/{filename}"
    
    # Try the constructed key first
    if unique_key in metadata:
        return metadata[unique_key]
    
    # If not found and we only have a filename, search all folders
    if "/" not in filename:
        for key, file_info in metadata.items():
            if key.endswith(f"/{filename}"):
                return file_info
    
    return None

def find_file_info(filename: str) -> Optional[Dict[str, Any]]:
    """
    Find file information by filename across all user folders
    
    Args:
        filename (str): The filename to search for
        
    Returns:
        dict or None: File metadata if found, None otherwise
    """
    metadata = load_metadata()
    
    # First try to find exact filename match
    for unique_key, file_info in metadata.items():
        if file_info.get("filename") == filename:
            return file_info
    
    # If not found, try to find by unique_key (folder/filename)
    if filename in metadata:
        return metadata[filename]
    
    return None

def get_file_original_path(filename: str) -> Optional[str]:
    """
    Get the original file path for a given filename
    
    Args:
        filename (str): The filename to find
        
    Returns:
        str or None: Full path to the original file if found, None otherwise
    """
    file_info = find_file_info(filename)
    if not file_info:
        return None
    
    folder = file_info.get("folder")
    if not folder:
        return None
    
    return os.path.join(UPLOADS_DIR, folder, filename)

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

def get_user_photos(username: str) -> List[Dict[str, Any]]:
    """
    Get photos from a specific user's folder
    
    Args:
        username (str): Username to get photos for
        
    Returns:
        list: List of dictionaries with file metadata from user's folder
    """
    metadata = load_metadata()
    result = []
    
    for unique_key, info in metadata.items():
        # Only include files from the user's folder
        if info.get("folder") == username:
            result.append(info)
    
    # Sort by upload date (newest first)
    result.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    return result

def get_global_photos() -> List[Dict[str, Any]]:
    """
    Get photos from the global shared folder
    
    Returns:
        list: List of dictionaries with file metadata from global folder
    """
    metadata = load_metadata()
    result = []
    
    for unique_key, info in metadata.items():
        # Only include files from the global folder
        if info.get("folder") == GLOBAL_FOLDER:
            result.append(info)
    
    # Sort by upload date (newest first)
    result.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    return result

def get_all_user_accessible_photos(username: str) -> List[Dict[str, Any]]:
    """
    Get all photos accessible to a user (their own + global)
    
    Args:
        username (str): Username to get accessible photos for
        
    Returns:
        list: List of dictionaries with file metadata accessible to user
    """
    metadata = load_metadata()
    result = []
    
    for unique_key, info in metadata.items():
        # Include files from user's folder or global folder
        if info.get("folder") == username or info.get("folder") == GLOBAL_FOLDER:
            result.append(info)
    
    # Sort by upload date (newest first)
    result.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    return result

def is_image(filename: str) -> bool:
    """
    Check if a file is an image based on its extension
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file is an image, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension and normalize
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # List of supported image extensions
    image_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'tif'}
    
    return ext in image_extensions

def ensure_thumbnails_dir(username: str) -> str:
    """
    Ensure the thumbnails directory exists for a user
    
    Args:
        username (str): Username to create thumbnails directory for
        
    Returns:
        str: Path to the thumbnails directory
    """
    thumbnails_dir = os.path.join(UPLOADS_DIR, username, "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)
    return thumbnails_dir

def generate_thumbnail(username: str, image_path: str, thumbnail_size: int = None) -> Optional[str]:
    """
    Generate a thumbnail for an image file
    
    Args:
        username (str): Username of the file owner
        image_path (str): Full path to the original image
        thumbnail_size (int): Maximum width/height for thumbnail (default: DEFAULT_THUMBNAIL_SIZE)
        
    Returns:
        str: Path to generated thumbnail, or None if generation failed
    """
    if thumbnail_size is None:
        thumbnail_size = DEFAULT_THUMBNAIL_SIZE
    try:
        # Ensure thumbnails directory exists
        thumbnails_dir = ensure_thumbnails_dir(username)
        
        # Get original filename
        filename = os.path.basename(image_path)
        
        # Create thumbnail path
        thumb_path = os.path.join(thumbnails_dir, filename)
        
        # Skip if thumbnail already exists
        if os.path.exists(thumb_path):
            logging.info(f"Thumbnail already exists for {filename}")
            return thumb_path
        
        # Open and process the image
        with Image.open(image_path) as img:
            # Handle images with EXIF orientation data
            img = ImageOps.exif_transpose(img)
            
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
            
            # Save thumbnail as JPEG with good quality
            img.save(thumb_path, 'JPEG', quality=85, optimize=True)
        
        logging.info(f"Generated thumbnail for {filename}: {thumb_path}")
        return thumb_path
        
    except Exception as e:
        logging.error(f"Failed to generate thumbnail for {image_path}: {str(e)}")
        return None

def get_thumbnail_path(username: str, filename: str) -> Optional[str]:
    """
    Get the path to a thumbnail file if it exists
    
    Args:
        username (str): Username of the file owner
        filename (str): Name of the original file
        
    Returns:
        str: Path to thumbnail if it exists, None otherwise
    """
    thumbnails_dir = os.path.join(UPLOADS_DIR, username, "thumbnails")
    thumb_path = os.path.join(thumbnails_dir, filename)
    
    return thumb_path if os.path.exists(thumb_path) else None

def delete_thumbnail(username: str, filename: str) -> bool:
    """
    Delete a thumbnail file if it exists
    
    Args:
        username (str): Username of the file owner
        filename (str): Name of the original file
        
    Returns:
        bool: True if thumbnail was deleted or didn't exist, False if deletion failed
    """
    try:
        thumbnail_path = get_thumbnail_path(username, filename)
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            logging.info(f"Deleted thumbnail for {filename}: {thumbnail_path}")
            return True
        # If thumbnail doesn't exist, that's still considered success
        return True
    except Exception as e:
        logging.error(f"Failed to delete thumbnail for {filename}: {str(e)}")
        return False

def update_photo_favorite_status(filename: str, username: str, is_favorite: bool) -> bool:
    """
    Update the favorite status of a photo
    
    Args:
        filename (str): Filename of the photo
        username (str): Username of the photo owner
        is_favorite (bool): New favorite status
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    metadata = load_metadata()
    unique_key = f"{username}/{filename}"
    
    if unique_key in metadata:
        metadata[unique_key]["is_favorite"] = is_favorite
        save_metadata(metadata)
        return True
    
    return False

def get_photos_paginated(
    username: Optional[str] = None,
    limit: int = 30,
    offset: int = 0,
    favorite: Optional[bool] = None,
    sort_by: str = "date",
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get paginated photos with filtering and sorting
    
    Args:
        username (str, optional): Filter by username (None for all accessible photos)
        limit (int): Number of photos to return (max 100)
        offset (int): Number of photos to skip
        favorite (bool, optional): Filter by favorite status
        sort_by (str): Sort field ("date", "name", "size")
        search (str, optional): Search in filename
        date_from (str, optional): Filter by date from (ISO format)
        date_to (str, optional): Filter by date to (ISO format)
        
    Returns:
        dict: Paginated results with photos and metadata
    """
    metadata = load_metadata()
    
    # Get all accessible photos
    if username:
        # User can see their own photos + global photos
        accessible_photos = []
        for unique_key, info in metadata.items():
            if info.get("folder") == username or info.get("folder") == GLOBAL_FOLDER:
                accessible_photos.append(info)
    else:
        # Admin can see all photos
        accessible_photos = list(metadata.values())
    
    # Apply filters
    filtered_photos = []
    for photo in accessible_photos:
        # Favorite filter
        if favorite is not None and photo.get("is_favorite", False) != favorite:
            continue
            
        # Search filter
        if search and search.lower() not in photo.get("filename", "").lower():
            continue
            
        # Date filters
        upload_date = photo.get("upload_date", "")
        if date_from and upload_date < date_from:
            continue
        if date_to and upload_date > date_to:
            continue
            
        filtered_photos.append(photo)
    
    # Sort photos
    if sort_by == "name":
        filtered_photos.sort(key=lambda x: x.get("filename", "").lower())
    elif sort_by == "size":
        filtered_photos.sort(key=lambda x: x.get("file_size", 0), reverse=True)
    else:  # Default to date
        filtered_photos.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
    
    # Apply pagination
    total_count = len(filtered_photos)
    limit = min(limit, 100)  # Cap at 100
    paginated_photos = filtered_photos[offset:offset + limit]
    
    # Format response with URLs
    photos_with_urls = []
    for photo in paginated_photos:
        photo_data = photo.copy()
        # Add URLs
        filename = photo_data.get("filename", "")
        photo_data["thumbnail_url"] = f"/thumbnails/{filename}" if photo_data.get("has_thumbnail") else None
        photo_data["original_url"] = f"/uploads/{photo_data.get('file_path', '')}"
        photos_with_urls.append(photo_data)
    
    return {
        "photos": photos_with_urls,
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total_count
    }
