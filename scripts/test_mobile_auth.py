#!/usr/bin/env python3
"""
Test mobile authentication endpoints to identify mobile-specific issues
"""

import requests
import json
import uuid

def test_mobile_auth():
    """Test authentication endpoints with mobile-like headers and data"""
    
    base_url = "https://art-app-production.up.railway.app"
    
    # Mobile-like headers
    mobile_headers = {
        "Origin": "https://myassemblage.art",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://myassemblage.art/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    print("🧪 Testing Mobile Authentication")
    print("=" * 50)
    
    # Test 1: Registration
    print("\n📱 Testing Mobile Registration...")
    unique_id = str(uuid.uuid4())[:8]
    register_data = {
        "username": f"mobileuser_{unique_id}",
        "password": "mobilepass123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            headers=mobile_headers,
            json=register_data,
            timeout=15
        )
        
        print(f"✅ Registration Status: {response.status_code}")
        print(f"✅ Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            register_result = response.json()
            print(f"✅ User ID: {register_result.get('user', {}).get('id', 'N/A')}")
            print(f"✅ Username: {register_result.get('user', {}).get('username', 'N/A')}")
            print(f"✅ Token: {register_result.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"❌ Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Test 2: Login with the same credentials
    print("\n🔐 Testing Mobile Login...")
    login_data = {
        "username": f"mobileuser_{unique_id}",
        "password": "mobilepass123"
    }
    
    try:
        # Login requires form-encoded data
        login_headers = mobile_headers.copy()
        login_headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        response = requests.post(
            f"{base_url}/auth/login",
            headers=login_headers,
            data=login_data,
            timeout=15
        )
        
        print(f"✅ Login Status: {response.status_code}")
        print(f"✅ Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            login_result = response.json()
            print(f"✅ User ID: {login_result.get('user', {}).get('id', 'N/A')}")
            print(f"✅ Username: {login_result.get('user', {}).get('username', 'N/A')}")
            print(f"✅ Token: {login_result.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 3: Test CORS preflight
    print("\n🌐 Testing CORS Preflight...")
    try:
        response = requests.options(
            f"{base_url}/auth/register",
            headers=mobile_headers,
            timeout=10
        )
        
        print(f"✅ OPTIONS Status: {response.status_code}")
        print(f"✅ CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"   {header}: {value}")
                
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n🎯 Mobile Authentication Test Complete!")

if __name__ == "__main__":
    test_mobile_auth()
