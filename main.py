from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
import shutil
from python import db_utils
from python import photo_utils
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Get JWT settings from environment variables
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure FastAPI to handle large file uploads
# This is done at the application level, separate from the server settings
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Configure photos directory based on environment
PHOTOS_BASE_DIR = os.environ.get("PHOTOS_PATH", "/mnt/photos")
if not os.path.exists(PHOTOS_BASE_DIR):
    # Fallback to local development path
    PHOTOS_BASE_DIR = "./photos"
    os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)

# Mount uploads first
app.mount("/uploads", StaticFiles(directory=PHOTOS_BASE_DIR), name="uploads")

# Serve React build files
react_build_path = "frontend/build"
if os.path.exists(react_build_path):
    # Mount React's static files (CSS, JS, etc.) at /static
    react_static_path = os.path.join(react_build_path, "static")
    if os.path.exists(react_static_path):
        app.mount("/static", StaticFiles(directory=react_static_path), name="react-static")
else:
    # Fallback to original static directory if React build doesn't exist
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Create photos directory and global folder if they don't exist
os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)
os.makedirs(os.path.join(PHOTOS_BASE_DIR, "global"), exist_ok=True)

# Use the password hashing context from db_utils
pwd_context = db_utils.pwd_context

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    admin: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FavoriteRequest(BaseModel):
    is_favorite: bool

def get_user(username: str):
    user_dict = db_utils.get_user(username)
    if user_dict:
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user_dict = db_utils.authenticate_user(username, password)
    if not user_dict:
        return False
    return UserInDB(**user_dict)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user info for React frontend"""
    user_dict = db_utils.get_user(current_user.username)
    if user_dict:
        # Split full_name into first_name and last_name
        full_name = user_dict.get("full_name", "")
        name_parts = full_name.split(" ", 1) if full_name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        return {
            "username": user_dict["username"],
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": user_dict.get("admin", False)
        }
    raise HTTPException(status_code=404, detail="User not found")

# Legacy HTML template routes - commented out in favor of React app
# @app.get("/", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, token: str = None):
    # First, check if token was provided in query parameters (from form submission)
    if token is None:
        # Check if token is in the Authorization header (from fetch with Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
    
    if token:
        try:
            # Verify the token manually
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = get_user(username)
                if user and not user.disabled:
                    # Check if user is an admin
                    if user.admin:
                        # Get files with metadata using the photo_utils module
                        files = photo_utils.get_all_files()
                        # Load all users to display in the admin panel
                        all_users = db_utils.load_users()
                        return templates.TemplateResponse("admin.html", {
                            "request": request, 
                            "files": files, 
                            "user": user,
                            "users": all_users,
                            "admin_username": db_utils.ADMIN_USERNAME
                        })
                    else:
                        # Redirect non-admin users to user view
                        return RedirectResponse(url="/user", status_code=303)
        except jwt.PyJWTError:
            pass
    
    # If we get here, authentication failed
    return RedirectResponse(url="/", status_code=303)

@app.get("/user", response_class=HTMLResponse)
async def user_page(request: Request, token: str = None):
    # First, check if token was provided in query parameters (from form submission)
    if token is None:
        # Check if token is in the Authorization header (from fetch with Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
    
    if token:
        try:
            # Verify the token manually
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = get_user(username)
                if user and not user.disabled:
                    # Get photos categorized by folder
                    my_photos = photo_utils.get_user_photos(username)
                    global_photos = photo_utils.get_global_photos()
                    all_photos = photo_utils.get_all_user_accessible_photos(username)
                    
                    return templates.TemplateResponse("user.html", {
                        "request": request, 
                        "user": user,
                        "my_photos": my_photos,
                        "global_photos": global_photos,
                        "all_photos": all_photos,
                        "my_photos_count": len(my_photos),
                        "global_photos_count": len(global_photos),
                        "total_photos_count": len(all_photos)
                    })
        except jwt.PyJWTError:
            pass
    
    # If we get here, authentication failed
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description="File to upload. Maximum size is 10GB"),
    token: str = None
):
    # First, check if token was provided in query parameters
    if token is None:
        # Check if token is in the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split("Bearer ")[1]
    
    # Authenticate using token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = get_user(username)
        if not user or user.disabled:
            raise HTTPException(status_code=401, detail="Invalid user")
        
        # Check file size - Now configured for much larger files
        # This is a fallback check as we've increased the limit using configuration
        MAX_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
        
        # File size check will happen during the upload, not before
        # We'll catch any exceptions from photo_utils if the file is too large
        try:
            # Diagnostic logging
            print(f"Processing upload for file: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
            
            # Make sure we have a file to process
            if not file or not hasattr(file, 'file'):
                raise ValueError("No file was provided or file object is invalid")
            
            # Get some file info for diagnostics
            try:
                file_position = file.file.tell()
                print(f"File position before upload: {file_position}")
            except Exception as pos_error:
                print(f"Error checking file position: {str(pos_error)}")
                
            # User is authenticated, process the file upload using photo_utils
            file_metadata = photo_utils.save_uploaded_file(file.file, file.filename, username)
            
            # For AJAX requests, return a JSON response
            if "application/json" in request.headers.get("Accept", ""):
                return {"success": True, "filename": file_metadata["filename"], "metadata": file_metadata}
            
            # For traditional form submissions, redirect
            return RedirectResponse(url="/admin", status_code=303)
            
        except IOError as io_error:
            # Handle file IO errors
            print(f"File IO error during upload: {str(io_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file: {str(io_error)}"
            )
        except Exception as e:
            # Handle other upload errors
            print(f"Upload error: {str(e)}")
            
            # Determine the appropriate status code
            if "too large" in str(e).lower():
                status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                detail = f"File too large: {str(e)}. Maximum file size is 10GB."
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                detail = f"Upload failed: {str(e)}"
                
            raise HTTPException(
                status_code=status_code,
                detail=detail
            )
            
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token signature")

# Remove the public registration endpoints - these will be deleted

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    admin: Optional[bool] = False

@app.post("/admin/create-user")
async def admin_create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user - only accessible by admins
    """
    # Check if the current user is an admin
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create new users"
        )
    
    success = db_utils.create_user(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        admin=user_data.admin
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Return success message
    return {
        "success": True,
        "message": f"User '{user_data.username}' created successfully",
        "admin": user_data.admin
    }

# Add route to get all users (for admin purposes only)
@app.get("/users")
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    # Only admin-level users should access this endpoint in production
    users = db_utils.load_users()
    return users

# Class for admin update request data
class AdminUpdateRequest(BaseModel):
    target_username: str
    admin_status: bool

@app.post("/api/update-admin-status")
async def update_admin_status(request: AdminUpdateRequest, current_user: User = Depends(get_current_active_user)):
    """
    Update the admin status of a user. Only the configured admin user can update admin status.
    """
    # Check if the current user is the admin user
    if current_user.username != db_utils.ADMIN_USERNAME:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"success": False, "message": f"Only {db_utils.ADMIN_USERNAME} can update admin privileges"}
        )
    
    # Call the db_utils function to update admin status
    if request.admin_status:
        success = db_utils.grant_admin_privileges(current_user.username, request.target_username)
    else:
        success = db_utils.revoke_admin_privileges(current_user.username, request.target_username)
    
    if success:
        return {"success": True, "message": f"Admin status for {request.target_username} has been updated"}
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": "Failed to update admin status"}
        )

@app.get("/photos")
async def get_photos(
    current_user: User = Depends(get_current_active_user),
    limit: int = 30,
    offset: int = 0,
    favorite: Optional[bool] = None,
    sort_by: str = "date",
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get paginated photos with filtering and sorting
    
    Query parameters:
    - limit: Number of photos to return (default: 30, max: 100)
    - offset: Number of photos to skip (default: 0)
    - favorite: Filter by favorite status (true/false)
    - sort_by: Sort field - "date", "name", or "size" (default: "date")
    - search: Search in filename
    - date_from: Filter by date from (ISO format)
    - date_to: Filter by date to (ISO format)
    """
    username = current_user.username if not current_user.admin else None
    
    return photo_utils.get_photos_paginated(
        username=username,
        limit=limit,
        offset=offset,
        favorite=favorite,
        sort_by=sort_by,
        search=search,
        date_from=date_from,
        date_to=date_to
    )

@app.get("/photos/global")
async def get_global_photos(current_user: User = Depends(get_current_active_user)):
    """Get global photos accessible to all users"""
    return photo_utils.get_global_photos()

@app.get("/photos/{filename}")
async def get_photo_info(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific photo including metadata
    """
    photo_info = photo_utils.get_file_info(filename, current_user.username)
    if not photo_info:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Check if user has permission to view this photo
    photo_folder = photo_info.get("folder")
    if not current_user.admin and photo_folder != current_user.username and photo_folder != "global":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Add URLs to response
    photo_data = photo_info.copy()
    photo_data["thumbnail_url"] = f"/thumbnails/{filename}" if photo_info.get("has_thumbnail") else None
    photo_data["original_url"] = f"/uploads/{photo_info.get('file_path', '')}"
    
    return photo_data

@app.delete("/photos/{filename}")
async def delete_photo(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a photo
    """
    username = current_user.username
    # ToDo: Check if user is admin and allow deletion of any photo
    success = photo_utils.delete_file(filename, username, current_user.admin)
    if not success:
        raise HTTPException(status_code=404, detail="Photo not found or permission denied")
    
    return {"message": "Photo deleted successfully"}

@app.get("/thumbnails/{filename}")
async def get_thumbnail(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get thumbnail for a photo
    """
    username = current_user.username
    is_admin = current_user.admin
    
    # For admin users, try to find the file in any user's folder
    if is_admin:
        # Find the file information to get the actual owner
        file_info = photo_utils.find_file_info(filename)
        if file_info:
            file_owner = file_info.get("uploaded_by") or file_info.get("folder")
            if file_owner:
                # Try to get thumbnail from the file owner's folder
                thumbnail_path = photo_utils.get_thumbnail_path(file_owner, filename)
                
                # If thumbnail doesn't exist, try to generate it
                if not thumbnail_path and photo_utils.is_image(filename):
                    original_file_path = photo_utils.get_file_original_path(filename)
                    if original_file_path and os.path.exists(original_file_path):
                        thumbnail_path = photo_utils.generate_thumbnail(file_owner, original_file_path)
                
                if thumbnail_path and os.path.exists(thumbnail_path):
                    return FileResponse(
                        thumbnail_path,
                        media_type="image/jpeg",
                        headers={"Cache-Control": "public, max-age=3600"}
                    )
    
    # Fallback to regular user logic or if admin logic fails
    thumbnail_path = photo_utils.get_thumbnail_path(username, filename)
    
    # Check if thumbnail exists
    if not thumbnail_path:
        # Try to generate thumbnail if it doesn't exist and it's an image
        if photo_utils.is_image(filename):
            # Get the original file path
            user_folder = photo_utils.get_user_folder_path(username)
            original_file_path = os.path.join(user_folder, filename)
            
            # Check if original file exists
            if os.path.exists(original_file_path):
                # Generate thumbnail
                thumbnail_path = photo_utils.generate_thumbnail(username, original_file_path)
                if not thumbnail_path:
                    raise HTTPException(status_code=500, detail="Failed to generate thumbnail")
            else:
                raise HTTPException(status_code=404, detail="Original file not found")
        else:
            raise HTTPException(status_code=404, detail="Thumbnail not available for this file type")
    
    # Verify the thumbnail file exists
    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    # Return the thumbnail file
    return FileResponse(
        thumbnail_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
    )

class BulkDeleteRequest(BaseModel):
    filenames: List[str]

@app.post("/photos/delete-multiple")
async def delete_multiple_photos(
    request: BulkDeleteRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete multiple photos in bulk
    """
    username = current_user.username
    successful_deletes = []
    failed_deletes = []
    
    for filename in request.filenames:
        try:
            success = photo_utils.delete_file(filename, username, current_user.admin)
            if success:
                successful_deletes.append(filename)
            else:
                failed_deletes.append({"filename": filename, "error": "File not found or permission denied"})
        except Exception as e:
            failed_deletes.append({"filename": filename, "error": str(e)})
    
    return {
        "success": len(failed_deletes) == 0,
        "deleted_count": len(successful_deletes),
        "failed_count": len(failed_deletes),
        "successful_deletes": successful_deletes,
        "failed_deletes": failed_deletes
    }

# Pydantic models for request/response
class PhotoFavoriteRequest(BaseModel):
    is_favorite: bool

@app.patch("/photos/{filename}/favorite")
async def toggle_photo_favorite(
    filename: str,
    request: FavoriteRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Toggle the favorite status of a photo
    
    Body parameters:
    - is_favorite: Boolean value to set favorite status
    """
    success = photo_utils.update_photo_favorite_status(
        filename=filename,
        username=current_user.username,
        is_favorite=request.is_favorite
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Photo not found or permission denied")
    
    return {
        "success": True,
        "filename": filename,
        "is_favorite": request.is_favorite,
        "message": f"Photo {'added to' if request.is_favorite else 'removed from'} favorites"
    }

# Additional API endpoints for React frontend
@app.post("/upload/global")
async def upload_global_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload file to global folder (admin only)"""
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        file_metadata = photo_utils.save_uploaded_file(file.file, file.filename, "global")
        return {"success": True, "filename": file_metadata["filename"], "metadata": file_metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/photos/global/{filename}")
async def delete_global_photo(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a global photo (admin only)"""
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = photo_utils.delete_file(filename, "global", True)
    if not success:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return {"message": "Photo deleted successfully"}

class UserRegistration(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str

@app.post("/register")
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    full_name = f"{user_data.first_name} {user_data.last_name}".strip()
    email = f"{user_data.username}@example.com"  # Default email
    
    success = db_utils.create_user(
        username=user_data.username,
        password=user_data.password,
        full_name=full_name,
        email=email,
        admin=False
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"success": True, "message": "User registered successfully"}

# Serve React app for all non-API routes
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_react_app(path: str):
    """Serve React app for any non-API route"""
    react_build_path = "frontend/build"
    index_file = os.path.join(react_build_path, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        # Fallback to basic HTML if React build doesn't exist
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Photo Server</title>
        </head>
        <body>
            <h1>React app not built yet</h1>
            <p>Please run: cd frontend && npm run build</p>
        </body>
        </html>
        """)