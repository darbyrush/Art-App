#!/usr/bin/env python3
"""
Simple debug script to test imports in the container environment.
Run this from the /app directory in the container.
"""

import sys
import os

print("🔍 Container Debug Information")
print("=" * 40)

print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
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
    print("Testing api.cors_config import...")
    from api.cors_config import get_cors_middleware
    print("✅ api.cors_config import successful")
    cors_middleware = get_cors_middleware()
    print("✅ get_cors_middleware() call successful")
except ImportError as e:
    print(f"❌ api.cors_config import failed: {e}")

try:
    print("Testing api.database.models import...")
    from api.database.models import User
    print("✅ api.database.models import successful")
except ImportError as e:
    print(f"❌ api.database.models import failed: {e}")

try:
    print("Testing api.schemas import...")
    from api.schemas import UserCreate
    print("✅ api.schemas import successful")
except ImportError as e:
    print(f"❌ api.schemas import failed: {e}")

print("\n�� Debug complete!")
