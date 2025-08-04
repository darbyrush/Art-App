#!/usr/bin/env python3
"""
Simple test script for Art Explorer API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running on port 8000")
        return False

def test_register():
    """Test user registration"""
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        if response.status_code == 200:
            print("✅ User registration successful")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login():
    """Test user login"""
    try:
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/token", data=data)
        if response.status_code == 200:
            print("✅ Login successful")
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_artwork_endpoint(token):
    """Test getting a random artwork"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/artworks/random", headers=headers)
        if response.status_code == 200:
            print("✅ Artwork endpoint working")
            return True
        else:
            print(f"❌ Artwork endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Artwork endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Art Explorer API")
    print("=" * 40)
    
    # Test health endpoint
    if not test_health():
        print("\n💡 To start the API, run:")
        print("uvicorn api.main:app --reload --port 8000")
        return
    
    # Test registration
    user_data = test_register()
    if not user_data:
        return
    
    # Test login
    token = test_login()
    if not token:
        return
    
    # Test artwork endpoint
    test_artwork_endpoint(token)
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("1. Start the Streamlit frontend: streamlit run app.py")
    print("2. Or use Docker: docker-compose up")

if __name__ == "__main__":
    main() 