#!/usr/bin/env python3
"""
Quick Environment Check Script
Run this to see what environment variables are currently set and what's missing.
"""

import os
from pathlib import Path

def check_env():
    """Check current environment configuration"""
    print("🔍 Art Explorer Environment Check")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Run: python setup_production_env.py")
        return
    
    # Load .env file
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    # Check critical variables
    critical_vars = {
        'ENVIRONMENT': 'Application environment',
        'SECRET_KEY': 'JWT secret key',
        'DATABASE_URL': 'Database connection string',
        'CORS_ORIGINS': 'Allowed CORS origins'
    }
    
    print("\n📋 Critical Environment Variables:")
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if value and not value.startswith('your_') and not value.startswith('https://your'):
            print(f"✅ {var}: {value[:20]}{'...' if len(value) > 20 else ''}")
        else:
            print(f"❌ {var}: {description} - NOT SET")
    
    # Check optional but recommended variables
    optional_vars = {
        'REDIS_URL': 'Redis connection for caching',
        'SMITHSONIAN_API_KEY': 'Smithsonian API access',
        'MET_API_KEY': 'Metropolitan Museum API access',
        'LOG_LEVEL': 'Logging level'
    }
    
    print("\n🔧 Optional Environment Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(f"✅ {var}: {value[:20]}{'...' if len(value) > 20 else ''}")
        else:
            print(f"⚠️  {var}: {description} - Not set (optional)")
    
    # Check production readiness
    print("\n🚀 Production Readiness:")
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        print("✅ Environment set to production")
    else:
        print(f"⚠️  Environment is '{env}' (should be 'production')")
    
    secret_key = os.getenv('SECRET_KEY', '')
    if secret_key and len(secret_key) >= 32 and not secret_key.startswith('your_'):
        print("✅ SECRET_KEY is properly configured")
    else:
        print("❌ SECRET_KEY needs to be set to a secure value")
    
    db_url = os.getenv('DATABASE_URL', '')
    if db_url and db_url.startswith('postgresql://'):
        print("✅ DATABASE_URL points to PostgreSQL")
    elif db_url and db_url.startswith('sqlite'):
        print("⚠️  DATABASE_URL uses SQLite (consider PostgreSQL for production)")
    else:
        print("❌ DATABASE_URL not properly configured")
    
    cors = os.getenv('CORS_ORIGINS', '')
    if cors and not cors.startswith('https://your'):
        print("✅ CORS_ORIGINS configured")
    else:
        print("❌ CORS_ORIGINS needs to be set to your actual domain")

if __name__ == "__main__":
    check_env()
