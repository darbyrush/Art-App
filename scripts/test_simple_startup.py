#!/usr/bin/env python3
"""
Simple startup test script to verify the application can start without import errors.
This tests the simplified import approach.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_imports():
    """Test the simplified import approach"""
    logger.info("🔍 Testing simplified imports...")
    
    try:
        # Test basic imports
        from fastapi import FastAPI
        logger.info("✅ FastAPI import successful")
    except ImportError as e:
        logger.error(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        # Test database imports with production paths
        from api.database.models import User, Artwork, Board
        logger.info("✅ api.database.models import successful")
    except ImportError as e:
        logger.error(f"❌ api.database.models import failed: {e}")
        return False
    
    try:
        from api.database.config import get_db, init_db, test_connection
        logger.info("✅ api.database.config import successful")
    except ImportError as e:
        logger.error(f"❌ api.database.config import failed: {e}")
        return False
    
    try:
        from api.schemas import UserCreate, UserResponse
        logger.info("✅ api.schemas import successful")
    except ImportError as e:
        logger.error(f"❌ api.schemas import failed: {e}")
        return False
    
    try:
        from api.services import UserService
        logger.info("✅ api.services import successful")
    except ImportError as e:
        logger.error(f"❌ api.services import failed: {e}")
        return False
    
    try:
        from api.auth import get_current_user, create_access_token, get_password_hash
        logger.info("✅ api.auth import successful")
    except ImportError as e:
        logger.error(f"❌ api.auth import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the FastAPI app can be created"""
    logger.info("🔍 Testing app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Art Explorer API",
            description="Simple Art Explorer API - Clean and Working",
            version="1.0.0"
        )
        
        # Test CORS configuration
        cors_origins_env = os.getenv("CORS_ORIGINS", "")
        cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
        
        default_origins = [
            "https://myassemblage.art",
            "https://www.myassemblage.art",
            "http://localhost:3000",
            "http://localhost:5173"
        ]
        
        all_origins = cors_origins + default_origins
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=all_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        logger.info("✅ FastAPI app creation successful")
        logger.info(f"✅ CORS origins configured: {all_origins}")
        return True
    except Exception as e:
        logger.error(f"❌ FastAPI app creation failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting simplified startup test...")
    
    # Test imports
    if not test_simple_imports():
        logger.error("❌ Import test failed")
        return False
    
    # Test app creation
    if not test_app_creation():
        logger.error("❌ App creation test failed")
        return False
    
    logger.info("🎉 All tests passed! Application should start successfully.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
