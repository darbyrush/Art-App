#!/usr/bin/env python3
"""
Test script to verify imports work correctly in the container environment.
This should be run from the /app directory in the container.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_container_imports():
    """Test imports that should work in the container"""
    logger.info("🔍 Testing container imports...")
    
    # Show current working directory and Python path
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    try:
        # Test importing from api directory
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
    
    try:
        from api.cors_config import get_cors_middleware
        logger.info("✅ api.cors_config import successful")
    except ImportError as e:
        logger.error(f"❌ api.cors_config import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the FastAPI app can be created"""
    logger.info("🔍 Testing app creation...")
    
    try:
        from fastapi import FastAPI
        from api.cors_config import get_cors_middleware
        
        app = FastAPI(
            title="Art Explorer API",
            description="Simple Art Explorer API - Clean and Working",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(get_cors_middleware())
        
        logger.info("✅ FastAPI app creation successful")
        return True
    except Exception as e:
        logger.error(f"❌ FastAPI app creation failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting container import test...")
    
    # Test imports
    if not test_container_imports():
        logger.error("❌ Import test failed")
        return False
    
    # Test app creation
    if not test_app_creation():
        logger.error("❌ App creation test failed")
        return False
    
    logger.info("🎉 All tests passed! Container should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
