#!/usr/bin/env python3
"""
Production Environment Setup Script
This script helps generate secure environment variables and validates production configuration.
"""

import secrets
import os
import sys
from pathlib import Path

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    return secrets.token_hex(length)

def create_env_file():
    """Create a .env file with secure defaults"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Aborted. Keeping existing .env file.")
            return
    
    # Generate secure secret key
    secret_key = generate_secret_key(32)
    
    env_content = f"""# Production Environment Configuration
# Generated automatically - REVIEW AND UPDATE THESE VALUES!

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
ENVIRONMENT=production
SECRET_KEY={secret_key}
DEBUG=false
LOG_LEVEL=INFO

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# PostgreSQL (Railway or other cloud provider)
DATABASE_URL=postgresql://username:password@host:port/database
# Alternative: Individual PostgreSQL settings
POSTGRES_HOST=your_postgres_host
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=art_explorer

# =============================================================================
# REDIS CONFIGURATION (for caching and sessions)
# =============================================================================
REDIS_URL=redis://username:password@host:port
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# =============================================================================
# CORS AND SECURITY
# =============================================================================
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# =============================================================================
# FILE UPLOADS
# =============================================================================
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads/profile_pictures

# =============================================================================
# API KEYS (External Services)
# =============================================================================
SMITHSONIAN_API_KEY=your_smithsonian_api_key
MET_API_KEY=your_met_api_key
HARVARD_API_KEY=your_harvard_api_key
CLEVELAND_API_KEY=your_cleveland_api_key
EUROPEANA_API_KEY=your_europeana_api_key

# =============================================================================
# MONITORING AND LOGGING
# =============================================================================
SENTRY_DSN=your_sentry_dsn_for_error_tracking
PROMETHEUS_ENABLED=true

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================
VITE_API_BASE_URL=https://your-backend-domain.com
NODE_ENV=production

# =============================================================================
# PERFORMANCE TUNING
# =============================================================================
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1024
KEEP_ALIVE_TIMEOUT=65
CLIENT_MAX_BODY_SIZE=10M

# =============================================================================
# DEVELOPMENT OVERRIDES (set to false in production)
# =============================================================================
DEVELOPMENT_MODE=false
ENABLE_DEBUG_ENDPOINTS=false
ENABLE_TEST_ENDPOINTS=false
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file with secure SECRET_KEY: {secret_key[:8]}...")
    print("⚠️  IMPORTANT: Review and update all placeholder values before deploying!")

def validate_env_file():
    """Validate that required environment variables are set"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    # Check required variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'CORS_ORIGINS'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your_') or os.getenv(var).startswith('https://your'):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or placeholder values for: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment validation passed!")
    return True

def main():
    print("🚀 Art Explorer Production Environment Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--validate':
        validate_env_file()
        return
    
    print("This script will:")
    print("1. Generate a secure SECRET_KEY")
    print("2. Create a .env file with production defaults")
    print("3. Set up proper environment configuration")
    print()
    
    response = input("Continue? (Y/n): ").lower()
    if response in ['n', 'no']:
        print("Aborted.")
        return
    
    create_env_file()
    print()
    print("🔧 Next steps:")
    print("1. Edit .env file with your actual values")
    print("2. Set DATABASE_URL to your PostgreSQL connection string")
    print("3. Update CORS_ORIGINS with your actual domain")
    print("4. Add your API keys for external services")
    print("5. Run: python setup_production_env.py --validate")
    print()
    print("📚 See PRODUCTION_README.md for detailed deployment instructions")

if __name__ == "__main__":
    main()
