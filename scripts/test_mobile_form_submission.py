#!/usr/bin/env python3
"""
Test mobile form submission to debug 422 error
"""

import requests
import json

def test_mobile_form_submission():
    """Test the exact form submission that's failing on mobile"""
    
    base_url = "https://art-app-production.up.railway.app"
    
    print("🧪 Testing Mobile Form Submission (422 Error Debug)")
    print("=" * 60)
    
    # Test 1: Test with exact OAuth2PasswordRequestForm format
    print("\n📝 Test 1: OAuth2PasswordRequestForm Format")
    print("-" * 40)
    
    # This is what the backend expects
    form_data = {
        'username': 'testuser123',
        'password': 'testpass123'
    }
    
    headers = {
        "Origin": "https://myassemblage.art",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=form_data,
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ 422 Error - Validation failed")
            print("Response details:", response.text)
        elif response.status_code == 200:
            print("✅ Success!")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test with URLSearchParams format (like frontend)
    print("\n🔗 Test 2: URLSearchParams Format")
    print("-" * 40)
    
    from urllib.parse import urlencode
    encoded_data = urlencode(form_data)
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=encoded_data,
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ 422 Error - Validation failed")
            print("Response details:", response.text)
        elif response.status_code == 200:
            print("✅ Success!")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test with JSON format (wrong format, but let's see the error)
    print("\n📄 Test 3: JSON Format (Wrong, but for comparison)")
    print("-" * 40)
    
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=form_data,
            headers=json_headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ 422 Error - This is expected for JSON")
            print("Response details:", response.text)
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test with missing fields
    print("\n🚫 Test 4: Missing Fields")
    print("-" * 40)
    
    incomplete_data = {
        'username': 'testuser123'
        # Missing password
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=incomplete_data,
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ 422 Error - Missing password field")
            print("Response details:", response.text)
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Test with empty fields
    print("\n🔍 Test 5: Empty Fields")
    print("-" * 40)
    
    empty_data = {
        'username': '',
        'password': ''
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            data=empty_data,
            headers=headers,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("❌ 422 Error - Empty fields")
            print("Response details:", response.text)
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎯 Form Submission Test Complete!")
    print("\n💡 If you see 422 errors, check the response details above")
    print("💡 The backend expects: username and password fields")
    print("💡 Content-Type should be: application/x-www-form-urlencoded")

if __name__ == "__main__":
    test_mobile_form_submission()
