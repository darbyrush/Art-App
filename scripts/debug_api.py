#!/usr/bin/env python3
"""
Debug script for Art Explorer API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def test_register_simple():
    """Test user registration with simple data"""
    try:
        data = {
            "username": "testuser2",
            "password": "testpass123"
        }
        print(f"Sending registration request: {data}")
        
        response = requests.post(
            f"{BASE_URL}/register", 
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration response: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def main():
    """Run debug tests"""
    print("🔍 Debugging Art Explorer API")
    print("=" * 40)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed")
        return
    
    # Test registration
    test_register_simple()

if __name__ == "__main__":
    main() 