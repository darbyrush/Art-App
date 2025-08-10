#!/usr/bin/env python3
"""
Test script for profile picture functionality
"""

import requests
import json
import os
from PIL import Image
import io

# API base URL
API_BASE = "http://localhost:8000"

def create_test_image():
    """Create a simple test image"""
    # Create a 100x100 test image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_profile_picture_upload():
    """Test the profile picture upload endpoint"""
    print("Testing profile picture upload...")
    
    # First, try to create a test user
    print("1. Creating test user...")
    test_user_data = {
        "username": "testuser_profile",
        "email": "test_profile@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/create-test-user", json=test_user_data)
        if response.status_code == 200:
            print("✓ Test user created successfully")
        else:
            print(f"⚠ Test user creation returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Error creating test user: {e}")
        return
    
    # Now try to login to get a token
    print("2. Logging in...")
    login_data = {
        "username": "testuser_profile",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✓ Login successful")
        else:
            print(f"✗ Login failed with status {response.status_code}: {response.text}")
            return
    except Exception as e:
        print(f"✗ Error during login: {e}")
        return
    
    # Test profile picture upload
    print("3. Testing profile picture upload...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test image
    test_image = create_test_image()
    
    files = {"file": ("test_image.jpg", test_image, "image/jpeg")}
    
    try:
        response = requests.post(
            f"{API_BASE}/users/me/profile-picture",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Profile picture upload successful!")
            print(f"  Message: {result.get('message')}")
            print(f"  Profile picture URL: {result.get('profile_picture_url')}")
            print(f"  User updated: {result.get('user', {}).get('username')}")
            
            # Test getting the profile picture
            print("4. Testing profile picture retrieval...")
            profile_url = result.get('profile_picture_url')
            if profile_url:
                full_url = f"{API_BASE}{profile_url}"
                img_response = requests.get(full_url)
                if img_response.status_code == 200:
                    print(f"✓ Profile picture retrieved successfully (size: {len(img_response.content)} bytes)")
                else:
                    print(f"✗ Failed to retrieve profile picture: {img_response.status_code}")
            
        else:
            print(f"✗ Profile picture upload failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error during profile picture upload: {e}")
    
    # Test profile picture deletion
    print("5. Testing profile picture deletion...")
    try:
        response = requests.delete(
            f"{API_BASE}/users/me/profile-picture",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Profile picture deletion successful!")
            print(f"  Message: {result.get('message')}")
        else:
            print(f"✗ Profile picture deletion failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error during profile picture deletion: {e}")

if __name__ == "__main__":
    print("Profile Picture Functionality Test")
    print("=" * 40)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✓ API is running and healthy")
            test_profile_picture_upload()
        else:
            print("✗ API is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Error checking API health: {e}")
    
    print("\nTest completed!")

