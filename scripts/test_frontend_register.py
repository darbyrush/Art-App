#!/usr/bin/env python3
"""
Test registration exactly as the frontend should send it after our changes
"""

import requests
import json
import uuid

def test_frontend_registration():
    """Test registration exactly as the frontend should send it"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/register"
    
    # Headers exactly as frontend would send
    headers = {
        "Origin": "https://art-nsws1hdkk-darbyrushs-projects.vercel.app",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://art-nsws1hdkk-darbyrushs-projects.vercel.app/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }
    
    # Data exactly as frontend should send (without email)
    unique_id = str(uuid.uuid4())[:8]
    test_data = {
        "username": f"testuser_{unique_id}",
        "password": "testpass123"
    }
    
    print("Testing Frontend Registration (new format)")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    print()
    
    try:
        # Test OPTIONS first
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
    test_frontend_registration() 