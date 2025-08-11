#!/usr/bin/env python3
"""
Railway Deployment Test Script
Tests the Railway backend deployment to diagnose 502 errors
"""

import requests
import time
import sys
from urllib.parse import urljoin

def test_railway_endpoints():
    """Test all Railway endpoints to diagnose issues"""
    
    # Railway production URL
    base_url = "https://art-app-production.up.railway.app"
    
    print("🚀 Testing Railway Backend Deployment")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print()
    
    # Test endpoints in order of complexity
    endpoints = [
        ("/startup-health", "Startup Health Check"),
        ("/ready", "Readiness Check"),
        ("/health", "Full Health Check"),
        ("/test", "Simple Test Endpoint"),
        ("/auth/login", "Login Endpoint (OPTIONS)")
    ]
    
    for endpoint, description in endpoints:
        print(f"🔍 Testing {description}: {endpoint}")
        
        try:
            # Test GET request first
            if endpoint == "/auth/login":
                # Test OPTIONS for CORS preflight
                response = requests.options(urljoin(base_url, endpoint), timeout=10)
                print(f"   OPTIONS: {response.status_code}")
            else:
                response = requests.get(urljoin(base_url, endpoint), timeout=10)
                print(f"   GET: {response.status_code}")
                
            if response.status_code == 200:
                print(f"   ✅ Success: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if 'status' in data:
                            print(f"   📊 Status: {data['status']}")
                        if 'database' in data:
                            print(f"   🗄️  Database: {data['database']}")
                    except:
                        pass
                print(f"   ⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📝 Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 10 seconds")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection Error - Service may be down")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request Error: {e}")
        except Exception as e:
            print(f"   💥 Unexpected Error: {e}")
        
        print()
        time.sleep(1)  # Small delay between requests
    
    print("=" * 50)
    print("🎯 Testing CORS Preflight")
    print()
    
    # Test CORS preflight specifically
    try:
        cors_response = requests.options(
            urljoin(base_url, "/auth/login"),
            headers={
                "Origin": "https://myassemblage.art",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=10
        )
        print(f"CORS Preflight Response: {cors_response.status_code}")
        print(f"CORS Headers:")
        for header, value in cors_response.headers.items():
            if header.lower().startswith('access-control'):
                print(f"  {header}: {value}")
    except Exception as e:
        print(f"CORS Test Error: {e}")
    
    print()
    print("=" * 50)
    print("📋 Summary")
    print()
    print("If you're getting 502 errors:")
    print("1. Check Railway logs for startup errors")
    print("2. Verify database connection string")
    print("3. Check environment variables are set")
    print("4. Ensure the app is starting without crashing")
    print()
    print("Common 502 causes:")
    print("- App crashing during startup")
    print("- Database connection failures")
    print("- Missing environment variables")
    print("- Health check timeouts")
    print("- Container resource limits")

if __name__ == "__main__":
    test_railway_endpoints()
