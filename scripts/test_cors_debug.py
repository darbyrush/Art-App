#!/usr/bin/env python3
"""
Test the /test endpoint to see current CORS configuration
"""

import requests
import json

def test_cors_config():
    """Test the /test endpoint to see current CORS configuration"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/test"
    
    headers = {
        "Origin": "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "User-Agent": "Test-Script/1.0"
    }
    
    print("Testing CORS Configuration")
    print("=" * 40)
    print(f"URL: {url}")
    print()
    
    try:
        # Test GET request
        print("Testing GET request...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cors_config() 