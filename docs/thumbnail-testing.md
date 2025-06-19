# Thumbnail Generation Testing Guide

## 🧪 Testing the Thumbnail Feature

### Prerequisites
1. Ensure Pillow is installed: `pip install pillow`
2. Make sure the `/mnt/photos` directory exists and is writable
3. Start the photo server: `./start_server.sh`

### Test Steps

#### 1. Upload an Image
```bash
# Login and get a token first
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"

# Upload an image file
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/test-image.jpg"
```

#### 2. Access the Thumbnail
```bash
# Get thumbnail (will auto-generate if doesn't exist)
curl -X GET "http://localhost:8000/thumbnails/test-image.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  --output thumbnail.jpg
```

#### 3. Verify Thumbnail Creation
Check that the thumbnail was created in the user's thumbnails folder:
```bash
ls -la /mnt/photos/your_username/thumbnails/
```

### Expected Behavior

1. **First thumbnail request**: 
   - Server generates 256px thumbnail
   - Saves it to `/mnt/photos/{username}/thumbnails/`
   - Returns JPEG thumbnail image

2. **Subsequent requests**:
   - Serves cached thumbnail directly
   - Much faster response time

3. **Non-image files**:
   - Returns 404 "Thumbnail not available for this file type"

4. **Missing files**:
   - Returns 404 "Original file not found"

### File Structure After Testing
```
/mnt/photos/
├── your_username/
│   ├── test-image.jpg          # Original uploaded file
│   └── thumbnails/
│       └── test-image.jpg      # Generated thumbnail (256px max)
└── metadata.json
```

### Performance Notes
- Thumbnails are generated asynchronously after upload
- Cached with 1-hour browser cache headers
- JPEG format with 85% quality for good compression
- Maintains aspect ratio (256px max width/height)

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
