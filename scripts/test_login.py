#!/usr/bin/env python3
"""
Test login endpoint
"""

import requests
import json

def test_login():
    """Test login endpoint"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/token"
    
    headers = {
        "Origin": "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Test-Script/1.0"
    }
    
    # Test data for the user we just created
    test_data = {
        "username": "testuser123",
        "password": "testpass123"
    }
    
    print("Testing Login Endpoint")
    print("=" * 30)
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {test_data}")
    print()
    
    try:
        # Test OPTIONS first
        print("Testing OPTIONS request...")
        response = requests.options(url, headers=headers, timeout=10)
        print(f"OPTIONS Status: {response.status_code}")
        print(f"OPTIONS Headers: {dict(response.headers)}")
        print()
        
        # Test POST
        print("Testing POST request...")
        response = requests.post(url, headers=headers, data=test_data, timeout=10)
        print(f"POST Status: {response.status_code}")
        print(f"POST Headers: {dict(response.headers)}")
        print(f"POST Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login() 