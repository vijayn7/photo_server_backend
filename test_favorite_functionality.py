#!/usr/bin/env python3
"""
Test script for the favorite button functionality
"""
import requests
import json

def test_favorite_functionality():
    """Test the favorite button functionality"""
    base_url = "http://192.168.68.10:8000"  # Replace with actual server URL
    
    # First, let's get a token by logging in
    login_data = {
        "username": "client1",  # Replace with actual username
        "password": "client1"  # Replace with actual password
    }
    
    print("Testing favorite button functionality...")
    
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
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get a list of photos first
        photos_response = requests.get(f"{base_url}/photos", headers=headers, params={"limit": 5})
        
        if photos_response.status_code != 200:
            print(f"Failed to get photos: {photos_response.status_code}")
            print(f"Response: {photos_response.text}")
            return
        
        photos_data = photos_response.json()
        photos = photos_data.get('photos', [])
        
        if not photos:
            print("No photos found to test favorite functionality")
            return
        
        # Test with the first photo
        test_photo = photos[0]
        photo_filename = test_photo['filename']
        initial_favorite_status = test_photo.get('is_favorite', False)
        
        print(f"Testing with photo: {photo_filename}")
        print(f"Initial favorite status: {initial_favorite_status}")
        
        # Test toggling favorite status
        new_favorite_status = not initial_favorite_status
        
        favorite_data = {
            "filename": photo_filename,
            "is_favorite": new_favorite_status
        }
        
        print(f"Setting favorite status to: {new_favorite_status}")
        
        # Make the favorite request
        favorite_response = requests.patch(
            f"{base_url}/photos/{photo_filename}/favorite", 
            headers=headers, 
            json={"is_favorite": new_favorite_status}
        )
        
        print(f"Favorite toggle response status: {favorite_response.status_code}")
        print(f"Favorite toggle response: {favorite_response.text}")
        
        if favorite_response.status_code == 200:
            result = favorite_response.json()
            print(f"✓ Favorite status updated successfully")
            print(f"New status: {result.get('is_favorite')}")
            
            # Verify the change by getting the photo again
            verify_response = requests.get(f"{base_url}/photos", headers=headers, params={"limit": 5})
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                updated_photo = next((p for p in verify_data['photos'] if p['filename'] == photo_filename), None)
                if updated_photo:
                    final_status = updated_photo.get('is_favorite', False)
                    print(f"Verified favorite status: {final_status}")
                    if final_status == new_favorite_status:
                        print("✓ Favorite status change verified successfully!")
                    else:
                        print("❌ Favorite status change not reflected in API")
                else:
                    print("❌ Could not find photo in verification response")
            
            # Test toggling back
            print(f"\nToggling back to original status: {initial_favorite_status}")
            
            restore_response = requests.patch(
                f"{base_url}/photos/{photo_filename}/favorite", 
                headers=headers, 
                json={"is_favorite": initial_favorite_status}
            )
            
            if restore_response.status_code == 200:
                print("✓ Successfully toggled favorite status back to original")
            else:
                print(f"❌ Failed to restore original favorite status: {restore_response.status_code}")
                print(f"Response: {restore_response.text}")
        
        else:
            print(f"❌ Favorite toggle failed: {favorite_response.status_code}")
            
            # Let's also test if the endpoint exists
            if favorite_response.status_code == 404:
                print("❌ The /toggle_favorite endpoint does not exist")
            elif favorite_response.status_code == 422:
                print("❌ Request validation error - check the request format")
                print("Expected format: {\"filename\": \"photo.jpg\", \"is_favorite\": true}")
            
        print("\n" + "="*50)
        print("Testing favorite filter in photos endpoint...")
        
        # Test the favorite filter
        favorite_filter_response = requests.get(
            f"{base_url}/photos", 
            headers=headers, 
            params={"limit": 10, "favorite": "true"}
        )
        
        if favorite_filter_response.status_code == 200:
            favorite_photos = favorite_filter_response.json()
            print(f"✓ Favorite filter works: {len(favorite_photos.get('photos', []))} favorite photos found")
        else:
            print(f"❌ Favorite filter failed: {favorite_filter_response.status_code}")
            print(f"Response: {favorite_filter_response.text}")
        
        print("\n✓ Favorite functionality test completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the server running on {base_url}?")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_favorite_functionality()
