#!/usr/bin/env python3
"""
Test script to verify that the FastAPI application can start without import errors.
This helps debug Railway deployment issues.
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all the imports that the main application needs"""
    logger.info("🔍 Testing imports...")
    
    try:
        # Test FastAPI imports
        from fastapi import FastAPI
        logger.info("✅ FastAPI import successful")
    except ImportError as e:
        logger.error(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        # Test database imports
        from database.models import User, Artwork, Board
        logger.info("✅ Database models import successful")
    except ImportError as e:
        logger.error(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from database.config import get_db, init_db, test_connection
        logger.info("✅ Database config import successful")
    except ImportError as e:
        logger.error(f"❌ Database config import failed: {e}")
        return False
    
    try:
        # Test API imports
        from schemas import UserCreate, UserResponse
        logger.info("✅ Schemas import successful")
    except ImportError as e:
        logger.error(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        from services import UserService
        logger.info("✅ Services import successful")
    except ImportError as e:
        logger.error(f"❌ Services import failed: {e}")
        return False
    
    try:
        from auth import get_current_user, create_access_token, get_password_hash
        logger.info("✅ Auth import successful")
    except ImportError as e:
        logger.error(f"❌ Auth import failed: {e}")
        return False
    
    try:
        from cors_config import get_cors_middleware
        logger.info("✅ CORS config import successful")
    except ImportError as e:
        logger.error(f"❌ CORS config import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the FastAPI app can be created"""
    logger.info("🔍 Testing app creation...")
    
    try:
        from fastapi import FastAPI
        from cors_config import get_cors_middleware
        
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

def test_environment():
    """Test environment variables"""
    logger.info("🔍 Testing environment...")
    
    # Check if we're in the right directory
    if not os.path.exists("api/main.py"):
        logger.error("❌ api/main.py not found. Please run from project root.")
        return False
    
    logger.info("✅ api/main.py found")
    
    # Check Python path
    logger.info(f"Python path: {sys.path}")
    
    # Check current working directory
    logger.info(f"Current working directory: {os.getcwd()}")
    
    return True

def main():
    """Main test function"""
    logger.info("🚀 Starting Railway deployment test...")
    
    # Test environment
    if not test_environment():
        logger.error("❌ Environment test failed")
        return False
    
    # Test imports
    if not test_imports():
        logger.error("❌ Import test failed")
        return False
    
    # Test app creation
    if not test_app_creation():
        logger.error("❌ App creation test failed")
        return False
    
    logger.info("🎉 All tests passed! Application should deploy successfully.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
