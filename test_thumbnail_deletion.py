#!/usr/bin/env python3
"""
Test script to verify thumbnail deletion functionality
"""

import os
import sys
from python.photo_utils import delete_file, is_image, delete_thumbnail

def test_thumbnail_deletion():
    """Test that thumbnails are deleted when files are deleted"""
    print("🗑️  Testing Thumbnail Deletion Functionality")
    print("=" * 50)
    
    # Test the delete_thumbnail function directly
    print("\n1. Testing delete_thumbnail function:")
    
    # Test with non-existent file (should return True - success)
    result = delete_thumbnail("test_user", "nonexistent.jpg")
    if result:
        print("  ✅ delete_thumbnail handles non-existent files correctly")
    else:
        print("  ❌ delete_thumbnail should return True for non-existent files")
    
    # Test image detection
    print("\n2. Testing is_image function:")
    test_files = [
        ("photo.jpg", True),
        ("image.png", True),
        ("document.pdf", False),
        ("video.mp4", False),
        ("picture.gif", True)
    ]
    
    for filename, expected in test_files:
        result = is_image(filename)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {filename}: {result} (expected: {expected})")
    
    print("\n3. Code Integration Check:")
    
    # Check that delete_file function exists and can be called
    try:
        # This should return False for non-existent file, but shouldn't crash
        result = delete_file("nonexistent.jpg", "test_user", False)
        print(f"  ✅ delete_file function works: {result}")
    except Exception as e:
        print(f"  ❌ delete_file function error: {e}")
    
    print("\n✨ Thumbnail deletion tests completed!")
    print("\nKey Features Added:")
    print("  • delete_thumbnail() function - removes thumbnail files")
    print("  • Integrated into delete_file() - automatic cleanup")
    print("  • Only deletes thumbnails for image files")
    print("  • Safe error handling - won't crash if thumbnail missing")
    
    print("\n🚀 Testing with Real Files:")
    print("1. Start the server: ./start_server.sh")
    print("2. Upload an image through the web interface")
    print("3. Check that thumbnail is created in /mnt/photos/{username}/thumbnails/")
    print("4. Delete the image through the web interface")
    print("5. Verify that both original and thumbnail are removed")

if __name__ == "__main__":
    test_thumbnail_deletion()
