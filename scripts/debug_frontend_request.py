#!/usr/bin/env python3
"""
Debug what the frontend is actually sending
"""

import requests
import json
import uuid

def debug_frontend_request():
    """Debug the frontend request to see what's causing the 400 error"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/register"
    
    # Test different possible data formats the frontend might be sending
    test_cases = [
        {
            "name": "Correct format (no email)",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": "testpass123"
            }
        },
        {
            "name": "With empty email (old format)",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": "testpass123",
                "email": ""
            }
        },
        {
            "name": "With null email",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}",
                "password": "testpass123",
                "email": None
            }
        },
        {
            "name": "Missing password",
            "data": {
                "username": f"testuser_{str(uuid.uuid4())[:8]}"
            }
        },
        {
            "name": "Empty username",
            "data": {
                "username": "",
                "password": "testpass123"
            }
        }
    ]
    
    headers = {
        "Origin": "https://art-nsws1hdkk-darbyrushs-projects.vercel.app",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
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
                print("❌ 400 Error - This might be what the frontend is sending!")
            elif response.status_code == 200:
                print("✅ Success")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    debug_frontend_request() 