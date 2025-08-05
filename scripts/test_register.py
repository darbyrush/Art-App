#!/usr/bin/env python3
"""
Test registration endpoint to see actual error details
"""

import requests
import json
import uuid

def test_registration():
    """Test registration endpoint"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/register"
    
    headers = {
        "Origin": "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "Content-Type": "application/json",
        "User-Agent": "Test-Script/1.0"
    }
    
    # Generate unique username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    test_data = {
        "username": f"testuser_{unique_id}",
        "password": "testpass123",
        "email": f"test_{unique_id}@example.com"
    }
    
    print("Testing Registration Endpoint")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {test_data}")
    print()
    
    try:
        # Test OPTIONS first with more detailed debugging
        print("Testing OPTIONS request...")
        response = requests.options(url, headers=headers, timeout=10)
        print(f"OPTIONS Status: {response.status_code}")
        print(f"OPTIONS Headers: {dict(response.headers)}")
        print(f"OPTIONS Response: {response.text}")
        print()
        
        # Test POST
        print("Testing POST request...")
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        print(f"POST Status: {response.status_code}")
        print(f"POST Headers: {dict(response.headers)}")
        print(f"POST Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration() 