#!/usr/bin/env python3
"""
Quick test to add some favorites and test the filter
"""
import requests
import json

def test_with_favorites():
    """Test favorite functionality with multiple photos"""
    base_url = "http://192.168.68.10:8000"
    
    login_data = {"username": "client1", "password": "client1"}
    
    print("Testing favorite filter with actual favorite photos...")
    
    try:
        # Login
        login_response = requests.post(f"{base_url}/token", data=login_data)
        token = login_response.json().get("access_token")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get photos
        photos_response = requests.get(f"{base_url}/photos", headers=headers, params={"limit": 3})
        photos = photos_response.json().get('photos', [])
        
        if len(photos) < 2:
            print("Need at least 2 photos for this test")
            return
        
        # Add first 2 photos to favorites
        for i in range(min(2, len(photos))):
            photo = photos[i]
            favorite_response = requests.patch(
                f"{base_url}/photos/{photo['filename']}/favorite", 
                headers=headers, 
                json={"is_favorite": True}
            )
            if favorite_response.status_code == 200:
                print(f"✓ Added {photo['filename']} to favorites")
            else:
                print(f"❌ Failed to add {photo['filename']} to favorites")
        
        # Test favorite filter
        favorite_filter_response = requests.get(
            f"{base_url}/photos", 
            headers=headers, 
            params={"limit": 10, "favorite": "true"}
        )
        
        if favorite_filter_response.status_code == 200:
            favorite_photos = favorite_filter_response.json()
            print(f"✓ Found {len(favorite_photos.get('photos', []))} favorite photos")
            
            for photo in favorite_photos.get('photos', []):
                print(f"  - {photo['filename']} (favorite: {photo.get('is_favorite')})")
        else:
            print(f"❌ Favorite filter failed: {favorite_filter_response.status_code}")
        
        # Clean up - remove favorites
        for i in range(min(2, len(photos))):
            photo = photos[i]
            cleanup_response = requests.patch(
                f"{base_url}/photos/{photo['filename']}/favorite", 
                headers=headers, 
                json={"is_favorite": False}
            )
            if cleanup_response.status_code == 200:
                print(f"✓ Removed {photo['filename']} from favorites")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_favorites()
