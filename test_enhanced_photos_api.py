#!/usr/bin/env python3
"""
Test script for the enhanced photos API endpoint
"""
import requests
import json

def test_enhanced_photos_api():
    """Test the enhanced photos API endpoint"""
    base_url = "http://192.168.68.10:8000"  # Replace with actual server URL
    
    # First, let's get a token by logging in
    login_data = {
        "username": "client1",  # Replace with actual username
        "password": "client1"  # Replace with actual password
    }
    
    print("Testing enhanced photos API endpoint...")
    
    try:
        # Login to get token
        login_response = requests.post(f"{base_url}/token", data=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("No access token received")
            return
        
        print("✓ Login successful, token obtained")
        
        # Test the enhanced photos endpoint
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test basic request
        params = {
            "limit": 10,
            "offset": 0,
            "sort_by": "date"
        }
        
        photos_response = requests.get(f"{base_url}/photos", headers=headers, params=params)
        
        if photos_response.status_code != 200:
            print(f"Photos API failed: {photos_response.status_code}")
            print(f"Response: {photos_response.text}")
            return
        
        photos_data = photos_response.json()
        print("✓ Enhanced photos API successful")
        print(f"Total photos: {photos_data.get('total', 0)}")
        print(f"Returned photos: {len(photos_data.get('photos', []))}")
        
        # Show first photo details if available
        if photos_data.get('photos'):
            first_photo = photos_data['photos'][0]
            print(f"\nFirst photo details:")
            print(f"  Filename: {first_photo.get('filename')}")
            print(f"  File path: {first_photo.get('file_path')}")
            print(f"  Thumbnail URL: {first_photo.get('thumbnail_url')}")
            print(f"  Original URL: {first_photo.get('original_url')}")
            print(f"  Is favorite: {first_photo.get('is_favorite')}")
            print(f"  Has metadata: {'metadata' in first_photo}")
            
            if 'metadata' in first_photo and first_photo['metadata']:
                metadata = first_photo['metadata']
                print(f"  Camera: {metadata.get('camera')}")
                print(f"  Has GPS: {metadata.get('has_gps')}")
        
        print("\n✓ Enhanced photos API test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the server running on {base_url}?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_photos_api()
