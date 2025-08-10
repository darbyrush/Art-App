#!/usr/bin/env python3
"""
Check Railway Environment Variables
This script helps identify what might be missing in your Railway deployment
"""

import os

def check_railway_environment():
    """Check what environment variables are needed vs what's available"""
    print("🔍 Railway Environment Variable Checker")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "SECRET_KEY": "Secret key for JWT tokens",
        "ENVIRONMENT": "Environment (production/development)",
        "CORS_ORIGINS": "Allowed CORS origins"
    }
    
    # Optional but recommended
    optional_vars = {
        "PORT": "Port number (Railway sets this automatically)",
        "RAILWAY_STATIC_URL": "Static file serving URL",
        "LOG_LEVEL": "Logging level"
    }
    
    print("\n📋 Required Environment Variables:")
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"   ✅ {var}: {description}")
            if var == "DATABASE_URL":
                # Mask the password in the URL
                url = os.getenv(var)
                if ":" in url and "@" in url:
                    parts = url.split("@")
                    if len(parts) == 2:
                        auth_part = parts[0].split(":")
                        if len(auth_part) >= 3:
                            masked_url = f"{auth_part[0]}:***@{parts[1]}"
                            print(f"      Value: {masked_url}")
                        else:
                            print(f"      Value: {url}")
                    else:
                        print(f"      Value: {url}")
                else:
                    print(f"      Value: {url}")
        else:
            print(f"   ❌ {var}: {description} - MISSING!")
    
    print("\n📋 Optional Environment Variables:")
    for var, description in optional_vars.items():
        if os.getenv(var):
            print(f"   ✅ {var}: {description}")
        else:
            print(f"   ⚠️  {var}: {description} - Not set (optional)")
    
    print("\n🔧 Railway-Specific Variables:")
    railway_vars = [k for k in os.environ.keys() if k.startswith("RAILWAY_")]
    if railway_vars:
        for var in railway_vars:
            print(f"   ℹ️  {var}: {os.getenv(var)}")
    else:
        print("   ℹ️  No Railway-specific variables found")
    
    print("\n🎯 Recommendations:")
    missing_vars = [var for var in required_vars.keys() if not os.getenv(var)]
    if missing_vars:
        print(f"   ❌ Missing required variables: {', '.join(missing_vars)}")
        print("   💡 Set these in your Railway project settings")
    else:
        print("   ✅ All required environment variables are set!")
    
    print("\n📚 Next Steps:")
    if missing_vars:
        print("1. Go to railway.app → Your Project → Variables")
        print("2. Add the missing environment variables")
        print("3. Redeploy your service")
    else:
        print("1. Environment variables look good")
        print("2. Check Railway logs for other issues")
        print("3. Try restarting the service")
    
    print("\n🌐 Test your backend:")
    print("   curl -v https://art-app-production.up.railway.app/health")

if __name__ == "__main__":
    check_railway_environment()
