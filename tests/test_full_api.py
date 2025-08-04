#!/usr/bin/env python3
"""
Comprehensive API test
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_full_flow():
    """Test the complete API flow"""
    print("🧪 Testing Complete API Flow")
    print("=" * 40)
    
    # Step 1: Register a user
    print("1. Registering user...")
    register_data = {
        "username": "testuser_api",
        "password": "testpass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/register", 
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ User registered successfully")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Step 2: Login to get token
    print("2. Logging in...")
    login_data = {
        "username": "testuser_api",
        "password": "testpass123"
    }
    
    response = requests.post(
        f"{BASE_URL}/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("✅ Login successful")
        print(f"Token: {access_token[:20]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Step 3: Test artwork endpoint
    print("3. Testing artwork endpoint...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/artworks/random",
        headers=headers
    )
    
    if response.status_code == 200:
        artwork = response.json()
        print("✅ Artwork fetched successfully!")
        print(f"Title: {artwork.get('title', 'Unknown')}")
        print(f"Artist: {artwork.get('artist', 'Unknown')}")
        print(f"Source: {artwork.get('source', 'Unknown')}")
        print(f"Image URL: {artwork.get('image_url', 'No image')[:50]}...")
    else:
        print(f"❌ Artwork fetch failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Step 4: Test user stats
    print("4. Testing user stats...")
    response = requests.get(
        f"{BASE_URL}/users/me/stats",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ User stats fetched successfully!")
        print(f"Total artworks: {stats.get('total_artworks', 0)}")
        print(f"Liked artworks: {stats.get('liked_artworks', 0)}")
        print(f"Unique museums: {stats.get('unique_museums', 0)}")
        print(f"Average rating: {stats.get('avg_rating', 0)}")
    else:
        print(f"❌ Stats fetch failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_full_flow() 