#!/usr/bin/env python3
"""
Simple test script to verify thumbnail functionality
"""

import os
import sys
from python.photo_utils import is_image, generate_thumbnail, get_thumbnail_path

def test_image_detection():
    """Test image file detection"""
    print("Testing image detection...")
    
    test_cases = [
        ("image.jpg", True),
        ("photo.jpeg", True),
        ("picture.png", True),
        ("graphic.webp", True),
        ("animation.gif", True),
        ("bitmap.bmp", True),
        ("document.pdf", False),
        ("video.mp4", False),
        ("text.txt", False),
        ("", False),
    ]
    
    for filename, expected in test_cases:
        result = is_image(filename)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {filename}: {result} (expected {expected})")
    
    print()

def test_thumbnail_dir():
    """Test thumbnail directory creation"""
    print("Testing thumbnail directory creation...")
    
    from python.photo_utils import ensure_thumbnails_dir
    
    test_username = "test_user"
    try:
        thumb_dir = ensure_thumbnails_dir(test_username)
        if os.path.exists(thumb_dir):
            print(f"  ✓ Thumbnail directory created: {thumb_dir}")
            # Clean up
            os.rmdir(thumb_dir)
            parent_dir = os.path.dirname(thumb_dir)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        else:
            print(f"  ✗ Failed to create thumbnail directory")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

def main():
    print("🖼️  Thumbnail Functionality Test")
    print("=" * 40)
    
    test_image_detection()
    test_thumbnail_dir()
    
    print("✨ Thumbnail tests completed!")
    print("\nTo test full functionality:")
    print("1. Start the server: ./start_server.sh")
    print("2. Upload an image file through the web interface")
    print("3. Access thumbnail via: GET /thumbnails/{filename}")

if __name__ == "__main__":
    main()
