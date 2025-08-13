#!/usr/bin/env python3
"""
Test password validation and other potential issues
"""

import requests
import json
import uuid

def test_password_validation():
    """Test different password scenarios that might cause 400 errors"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/register"
    
    headers = {
        "Origin": "https://art-nsws1hdkk-darbyrushs-projects.vercel.app",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    test_cases = [
        {
            "name": "Short password",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": "123"
            }
        },
        {
            "name": "Empty password",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": ""
            }
        },
        {
            "name": "Password with special chars",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": "test@123!"
            }
        },
        {
            "name": "Username with special chars",
            "data": {
                "username": f"test.user_{str(uuid.uuid4())[:8]}",
                "password": "testpass123"
            }
        },
        {
            "name": "Very long username",
            "data": {
                "username": "a" * 100,
                "password": "testpass123"
            }
        },
        {
            "name": "Username with spaces",
            "data": {
                "username": "test user",
                "password": "testpass123"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'], timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("❌ 400 Error - This might be the issue!")
            elif response.status_code == 200:
                print("✅ Success")
            elif response.status_code == 422:
                print("⚠️ Validation Error")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_password_validation() 