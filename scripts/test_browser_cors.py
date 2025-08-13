#!/usr/bin/env python3
"""
Test CORS preflight request exactly as a browser would send it
"""

import requests
import json

def test_browser_preflight():
    """Test OPTIONS request exactly as a browser would send it"""
    
    base_url = "https://art-app-production.up.railway.app"
    url = f"{base_url}/register"
    
    # Test different origins
    test_origins = [
        "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "https://example.com",
        "http://localhost:3000",
        "https://vercel.app"
    ]
    
    for origin in test_origins:
        print(f"\nTesting with origin: {origin}")
        print("=" * 50)
        
        # Headers that a browser typically sends in a preflight request
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        try:
            # Test OPTIONS request exactly as browser would send
            print("Testing OPTIONS request (browser-style)...")
            response = requests.options(url, headers=headers, timeout=10)
            print(f"OPTIONS Status: {response.status_code}")
            print(f"OPTIONS Headers: {dict(response.headers)}")
            print(f"OPTIONS Response: {response.text}")
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_browser_preflight() 