# Photo Server Backend

A robust FastAPI-based backend service for storing, managing, and serving photos and other files. This server provides user authentication, role-based access control, and secure file operations in a multi-user environment.

## Features

### Authentication & User Management
- **JWT-based Authentication** - Secure token-based authentication system
- **Role-Based Access Control** - Admin and regular user roles with different privileges
- **User Management** - Create, view, and manage user accounts (admin only)
- **Admin Privileges** - Special privileges for administrative users

### File Management
- **File Upload** - Support for large file uploads up to 10GB
- **User-Specific Folders** - Each user has their own private folder for uploads
- **Global Shared Folder** - Common area accessible to all users
- **File Metadata** - Automatically tracks file information including size, type, and upload date
- **Image & Video Support** - Special handling for image and video file types

### Web Interface
- **Admin Dashboard** - Complete administrative control panel
- **User Dashboard** - User-friendly interface for managing personal files
- **Responsive Design** - Works on desktop and mobile devices

## Technical Specifications

### System Requirements
- Python 3.8 or higher
- At least 512MB RAM (1GB+ recommended for large file uploads)
- Disk space requirements dependent on your storage needs

### Dependencies
- FastAPI - High-performance web framework
- Uvicorn - ASGI server implementation
- Passlib - Password hashing library with bcrypt support
- PyJWT - JSON Web Token implementation
- Jinja2 - Template engine for HTML rendering
- Python-multipart - For handling form data and file uploads

## Installation

1. Clone the repository:
   ```bash
   git clone https://your-repository-url.git
   cd photo_server_backend
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional):
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   PHOTO_SERVER_ADMIN=admin_username
   PHOTO_SERVER_ADMIN_PASSWORD=admin_password
   ```

4. Run the server:
   ```bash
   ./start_server.sh
   ```

## API Endpoints

### Authentication

#### `POST /token`
- **Purpose**: Log in and get an access token
- **Parameters**:
  - `username`: User's username
  - `password`: User's password
- **Response**: JSON object containing access token and token type
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=alice&password=secret"
  ```

### User Management

#### `GET /users/me`
- **Purpose**: Get information about the currently logged-in user
- **Authentication**: Requires valid token
- **Response**: JSON object with user details
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/users/me" \
    -H "Authorization: Bearer your_access_token"
  ```

#### `GET /users`
- **Purpose**: Get all users in the system
- **Authentication**: Requires valid token with admin privileges
- **Response**: List of user objects
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/users" \
    -H "Authorization: Bearer your_access_token"
  ```

#### `POST /admin/create-user`
- **Purpose**: Create a new user (admin only)
- **Authentication**: Requires valid token with admin privileges
- **Parameters**:
  - `username`: New user's username
  - `email`: New user's email
  - `full_name`: New user's full name
  - `password`: New user's password
  - `admin`: Boolean indicating if user should have admin privileges
- **Response**: JSON object with success status and message
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/admin/create-user" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your_access_token" \
    -d '{
      "username": "newuser",
      "email": "newuser@example.com",
      "full_name": "New User",
      "password": "password123",
      "admin": false
    }'
  ```

#### `POST /api/update-admin-status`
- **Purpose**: Grant or revoke admin privileges for a user
- **Authentication**: Requires valid token with master admin privileges
- **Parameters**:
  - `target_username`: Username of the user to update
  - `admin_status`: Boolean indicating new admin status
- **Response**: JSON object with success status and message
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/update-admin-status" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your_access_token" \
    -d '{
      "target_username": "user123",
      "admin_status": true
    }'
  ```

### File Management

#### `POST /upload`
- **Purpose**: Upload a file to the server
- **Authentication**: Requires valid token
- **Parameters**:
  - `file`: The file to upload (multipart/form-data)
  - `token`: Authentication token (can be provided in Authorization header instead)
- **Response**: JSON object with file metadata
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/upload" \
    -H "Authorization: Bearer your_access_token" \
    -F "file=@/path/to/your/file.jpg"
  ```

#### `GET /photos`
- **Purpose**: Get list of photos accessible to the current user
- **Authentication**: Requires valid token
- **Response**: List of photo metadata objects
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/photos" \
    -H "Authorization: Bearer your_access_token"
  ```

#### `GET /photos/{filename}`
- **Purpose**: Get information about a specific photo
- **Authentication**: Requires valid token
- **Parameters**:
  - `filename`: Name of the file to get information about
- **Response**: JSON object with photo metadata
- **Example**:
  ```bash
  curl -X GET "http://localhost:8000/photos/example.jpg" \
    -H "Authorization: Bearer your_access_token"
  ```

#### `DELETE /photos/{filename}`
- **Purpose**: Delete a photo
- **Authentication**: Requires valid token
- **Parameters**:
  - `filename`: Name of the file to delete
- **Response**: JSON object confirming deletion
- **Example**:
  ```bash
  curl -X DELETE "http://localhost:8000/photos/example.jpg" \
    -H "Authorization: Bearer your_access_token"
  ```

#### `POST /photos/delete-multiple`
- **Purpose**: Delete multiple photos in bulk
- **Authentication**: Requires valid token
- **Parameters**:
  - JSON object with `filenames` array
- **Response**: JSON object with deletion results
- **Example**:
  ```bash
  curl -X POST "http://localhost:8000/photos/delete-multiple" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your_access_token" \
    -d '{
      "filenames": ["photo1.jpg", "photo2.png"]
    }'
  ```

### Web Interface Routes

#### `GET /`
- **Purpose**: Login page
- **Authentication**: None
- **Response**: HTML login page

#### `GET /admin`
- **Purpose**: Admin dashboard
- **Authentication**: Requires valid token with admin privileges
- **Response**: HTML admin dashboard page

#### `GET /user`
- **Purpose**: User dashboard
- **Authentication**: Requires valid token
- **Response**: HTML user dashboard page

## File Storage Structure

- `/mnt/photos/` - Main uploads directory
  - `/mnt/photos/global/` - Global shared folder accessible to all users
  - `/mnt/photos/{username}/` - User-specific folders for private uploads
  - `/mnt/photos/metadata.json` - File containing metadata for all uploads

## Security Features

- JWT-based authentication with configurable expiration
- Bcrypt password hashing
- Role-based access control for endpoints
- User-specific folders to prevent unauthorized access

## Configuration Options

Configuration can be set via environment variables or a `.env` file:

- `SECRET_KEY`: Secret key for JWT token signing (default: "your-secret-key")
- `ALGORITHM`: JWT signing algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token validity period in minutes (default: 30)
- `PHOTO_SERVER_ADMIN`: Username of the master admin account (default: "vijayn7")
- `PHOTO_SERVER_ADMIN_PASSWORD`: Password for the master admin account (default: "admin_password")

## Performance Optimizations

- Configurable for large file uploads (up to 10GB)
- Chunk-based file upload processing
- Increased timeout settings for handling large files
- Metadata caching to avoid redundant file system operations

## Troubleshooting

For common issues, check the documentation in the `docs/` folder:
- `env-troubleshooting.md` - Solutions for environment and configuration issues
- `upload-troubleshooting.md` - Solutions for file upload problems