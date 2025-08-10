#!/usr/bin/env python3
"""
Test script to verify Railway backend connection
Run this after deploying your backend to Railway
"""

import requests
import sys
import os

def test_railway_backend(api_url):
    """Test the Railway backend connection"""
    print(f"🔍 Testing Railway backend connection to: {api_url}")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{api_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {health_response.json()}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    try:
        # Test CORS preflight
        print("\n2. Testing CORS preflight...")
        cors_response = requests.options(
            f"{api_url}/token",
            headers={
                "Origin": "https://myassemblage.art",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        if cors_response.status_code == 200:
            print("✅ CORS preflight passed")
            cors_headers = cors_response.headers
            print(f"   Access-Control-Allow-Origin: {cors_headers.get('Access-Control-Allow-Origin', 'Not set')}")
            print(f"   Access-Control-Allow-Methods: {cors_headers.get('Access-Control-Allow-Methods', 'Not set')}")
        else:
            print(f"❌ CORS preflight failed: {cors_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
    
    try:
        # Test API endpoint
        print("\n3. Testing API endpoint...")
        api_response = requests.get(f"{api_url}/test", timeout=10)
        if api_response.status_code == 200:
            print("✅ API endpoint accessible")
            print(f"   Response: {api_response.json()}")
        else:
            print(f"❌ API endpoint failed: {api_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Update your frontend VITE_API_BASE_URL with this backend URL")
    print("2. Deploy your frontend to Railway")
    print("3. Test the full application")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_railway_connection.py <RAILWAY_BACKEND_URL>")
        print("Example: python test_railway_connection.py https://your-service.railway.app")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    test_railway_backend(api_url)
