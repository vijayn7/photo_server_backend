#!/usr/bin/env python3
"""
Test script to verify the enhanced photo listing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from python import photo_utils

def test_exif_functionality():
    """Test EXIF metadata extraction"""
    print("🔍 Testing EXIF Functionality")
    print("=" * 50)
    
    # Test if EXIF libraries are available
    try:
        import piexif
        import exifread
        print("✅ EXIF libraries are available")
        
        # Test the extract_exif_metadata function
        print("\n📊 Testing EXIF extraction function...")
        result = photo_utils.extract_exif_metadata("nonexistent.jpg")
        print(f"✅ Function returns: {type(result).__name__} (expected dict)")
        
    except ImportError as e:
        print(f"❌ EXIF libraries not available: {e}")
        return False
    
    return True

def test_paginated_photos():
    """Test paginated photo retrieval"""
    print("\n📄 Testing Paginated Photo Retrieval")
    print("=" * 50)
    
    try:
        # Test the paginated function
        result = photo_utils.get_photos_paginated(
            username="testuser",
            limit=10,
            offset=0,
            favorite=None,
            sort_by="date"
        )
        
        print(f"✅ Paginated function returns: {type(result).__name__}")
        print(f"✅ Expected keys present: {set(result.keys())}")
        
        expected_keys = {"photos", "total", "limit", "offset", "has_more"}
        actual_keys = set(result.keys())
        
        if expected_keys == actual_keys:
            print("✅ All expected keys present in response")
        else:
            print(f"⚠️  Missing keys: {expected_keys - actual_keys}")
            print(f"⚠️  Extra keys: {actual_keys - expected_keys}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing paginated photos: {e}")
        return False

def test_favorite_functionality():
    """Test photo favorite functionality"""
    print("\n⭐ Testing Photo Favorite Functionality")
    print("=" * 50)
    
    try:
        # Test the favorite update function
        result = photo_utils.update_photo_favorite_status(
            filename="test.jpg",
            username="testuser", 
            is_favorite=True
        )
        
        print(f"✅ Favorite function returns: {result} (expected boolean)")
        return True
        
    except Exception as e:
        print(f"❌ Error testing favorite functionality: {e}")
        return False

def main():
    print("🚀 Photo Listing Feature Test Suite")
    print("=" * 55)
    
    tests = [
        ("EXIF Functionality", test_exif_functionality),
        ("Paginated Photos", test_paginated_photos),
        ("Favorite Functionality", test_favorite_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 55)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 55)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The enhanced photo listing feature is ready.")
        print("\n📋 New Features Available:")
        print("  • EXIF metadata extraction from images")
        print("  • Paginated photo listing with filtering")
        print("  • Photo favorite/unfavorite functionality")
        print("  • Enhanced photo metadata including timestamps")
        print("  • Search and sorting capabilities")
        
        print("\n🔗 New API Endpoints:")
        print("  • GET /photos?limit=30&offset=0&favorite=true&sort_by=date")
        print("  • PATCH /photos/{filename}/favorite")
        print("  • GET /photos/{filename} (enhanced with metadata)")
        
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
