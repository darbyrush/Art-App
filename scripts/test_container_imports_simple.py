#!/usr/bin/env python3
"""
Simple container import test script.
This tests the basic imports that the container needs to work.
"""

import sys
import os

print("🔍 Container Import Test")
print("=" * 30)

print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

print("\n📁 Directory contents:")
for item in os.listdir('.'):
    print(f"  - {item}")

if os.path.exists('api'):
    print("\n📁 API directory contents:")
    for item in os.listdir('api'):
        print(f"  - {item}")

print("\n🔍 Testing imports...")

try:
    print("Testing FastAPI import...")
    from fastapi import FastAPI
    print("✅ FastAPI import successful")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    print("Testing api.schemas import...")
    from api.schemas import UserCreate, UserResponse
    print("✅ api.schemas import successful")
except ImportError as e:
    print(f"❌ api.schemas import failed: {e}")

try:
    print("Testing api.database.models import...")
    from api.database.models import User, Artwork, Board
    print("✅ api.database.models import successful")
except ImportError as e:
    print(f"❌ api.database.models import failed: {e}")

try:
    print("Testing api.database.config import...")
    from api.database.config import get_db, init_db, test_connection
    print("✅ api.database.config import successful")
except ImportError as e:
    print(f"❌ api.database.config import failed: {e}")

try:
    print("Testing api.services import...")
    from api.services import UserService
    print("✅ api.services import successful")
except ImportError as e:
    print(f"❌ api.services import failed: {e}")

try:
    print("Testing api.auth import...")
    from api.auth import get_current_user, create_access_token, get_password_hash
    print("✅ api.auth import successful")
except ImportError as e:
    print(f"❌ api.auth import failed: {e}")

print("\n🎯 Test complete!")
