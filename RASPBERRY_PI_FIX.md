# 🔧 Raspberry Pi Upload Error Fix

## Issue Description
The server was experiencing two main issues on Raspberry Pi:
1. **Permission Error**: `PermissionError: [Errno 13] Permission denied: '/mnt/photos/global'`
2. **Async/Await Error**: `AttributeError: 'coroutine' object has no attribute 'disabled'`

## ✅ Fixes Applied

### 1. **Fixed Async/Await Issue in Upload Function**
**Problem**: In `main.py` line 251, `get_user(username)` was called without `await`
**Solution**: Changed to `user = await get_user(username)`

```python
# BEFORE (line 251)
user = get_user(username)

# AFTER (line 251) 
user = await get_user(username)
```

### 2. **Made Upload Directory Configurable**
**Problem**: Hard-coded path `/mnt/photos` causing permission issues
**Solution**: Made paths configurable via environment variables

#### Changes in `python/photo_utils.py`:
```python
# BEFORE
UPLOADS_DIR = "/mnt/photos"

# AFTER
UPLOADS_DIR = os.environ.get("PHOTOS_UPLOAD_DIR", "./photos")
```

#### Changes in `main.py`:
```python
# BEFORE
app.mount("/uploads", StaticFiles(directory="./photos"), name="uploads")
os.makedirs("./photos", exist_ok=True)
os.makedirs("./photos/global", exist_ok=True)

# AFTER
PHOTOS_UPLOAD_DIR = os.environ.get("PHOTOS_UPLOAD_DIR", "./photos")
app.mount("/uploads", StaticFiles(directory=PHOTOS_UPLOAD_DIR), name="uploads")
os.makedirs(PHOTOS_UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(PHOTOS_UPLOAD_DIR, "global"), exist_ok=True)
```

## 🚀 Deployment Options for Raspberry Pi

### Option 1: Use Default Local Directory (Recommended)
The server will now use `./photos` by default, which should work without permission issues.

**No additional configuration needed** - just restart the server.

### Option 2: Configure Custom Directory
Set the environment variable to specify a custom upload directory:

```bash
# Set environment variable
export PHOTOS_UPLOAD_DIR="/home/vnannapu/photos"

# Or add to .env file
echo "PHOTOS_UPLOAD_DIR=/home/vnannapu/photos" >> .env

# Restart the server
sudo systemctl restart photo-server
```

### Option 3: Fix Permissions for /mnt/photos (If you want to keep the original path)
```bash
# Create the directory with proper permissions
sudo mkdir -p /mnt/photos/global
sudo chown -R vnannapu:vnannapu /mnt/photos
sudo chmod -R 755 /mnt/photos

# Then set the environment variable
export PHOTOS_UPLOAD_DIR="/mnt/photos"
```

## 🔄 How to Deploy the Fix

### 1. Update the Code on Raspberry Pi
```bash
# Navigate to your project directory
cd /home/vnannapu/photo-server

# Pull the latest changes or copy the updated files
# Make sure main.py and python/photo_utils.py have the fixes

# If using git:
git pull origin main

# Or manually copy the fixed files
```

### 2. Restart the Service
```bash
# Restart the systemd service
sudo systemctl restart photo-server

# Check status
sudo systemctl status photo-server

# Check logs
sudo journalctl -u photo-server -f
```

### 3. Test the Upload
Try uploading a file through the web interface to verify the fix works.

## 📝 Environment Variable Reference

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `PHOTOS_UPLOAD_DIR` | `./photos` | Directory where uploaded files are stored |
| `SECRET_KEY` | `your-secret-key` | JWT signing key |
| `PHOTO_SERVER_ADMIN` | `vijayn7` | Admin username |
| `PHOTO_SERVER_ADMIN_PASSWORD` | `admin_password` | Admin password |

## 🧪 Testing

After applying the fix, test these scenarios:
1. ✅ **Upload a file** - Should work without permission errors
2. ✅ **Check file storage** - Files should be saved in the configured directory
3. ✅ **View uploaded files** - Files should be accessible via the web interface
4. ✅ **Admin functions** - User management should work properly

## 📋 Troubleshooting

If you still encounter issues:

1. **Check directory permissions**:
   ```bash
   ls -la /path/to/your/upload/directory
   ```

2. **Check service logs**:
   ```bash
   sudo journalctl -u photo-server -n 50
   ```

3. **Verify environment variables**:
   ```bash
   systemctl show photo-server | grep Environment
   ```

4. **Test the fixed endpoint**:
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -H "Authorization: Bearer your_token" \
     -F "file=@test.jpg"
   ```

---

**✅ These fixes should resolve both the permission error and the async/await error you were experiencing.**
