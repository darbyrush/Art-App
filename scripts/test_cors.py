#!/usr/bin/env python3
"""
Test CORS configuration for the Art App API
"""

import requests
import json

def test_cors_configuration():
    """Test CORS configuration with different origins"""
    
    # Test URLs
    base_url = "https://art-app-production.up.railway.app"
    test_urls = [
        f"{base_url}/test",
        f"{base_url}/register",
        f"{base_url}/health"
    ]
    
    # Test origins
    test_origins = [
        "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://example.com"
    ]
    
    print("Testing CORS Configuration")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        print("-" * 30)
        
        for origin in test_origins:
            try:
                headers = {
                    "Origin": origin,
                    "User-Agent": "CORS-Test-Script/1.0",
                    "Content-Type": "application/json"
                }
                
                # Test OPTIONS request (preflight)
                print(f"  Testing OPTIONS request from {origin}")
                response = requests.options(url, headers=headers, timeout=10)
                
                print(f"    Status: {response.status_code}")
                print(f"    Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
                print(f"    Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
                print(f"    Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
                
                # Test POST request for registration
                if "register" in url:
                    print(f"  Testing POST request from {origin}")
                    test_data = {
                        "username": "testuser",
                        "password": "testpass123",
                        "email": "test@example.com"
                    }
                    response = requests.post(url, headers=headers, json=test_data, timeout=10)
                else:
                    # Test GET request
                    print(f"  Testing GET request from {origin}")
                    response = requests.get(url, headers=headers, timeout=10)
                
                print(f"    Status: {response.status_code}")
                print(f"    Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"    Response: {response.text[:200]}...")
                elif response.status_code == 422:
                    print(f"    Response: Validation error (expected for test data)")
                elif response.status_code == 409:
                    print(f"    Response: User already exists (expected)")
                
            except requests.exceptions.RequestException as e:
                print(f"    Error: {e}")
            
            print()

if __name__ == "__main__":
    test_cors_configuration() 