#!/usr/bin/env python3
"""
Fix Dependencies for Railway Deployment
This script checks and fixes common dependency issues
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description} successful")
            return True
        else:
            print(f"   ❌ {description} failed:")
            print(f"      {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ {description} error: {e}")
        return False

def check_dependencies():
    """Check and fix dependencies"""
    print("🔍 Railway Dependency Checker")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend/requirements.txt"):
        print("❌ Error: backend/requirements.txt not found")
        print("   Please run this script from the project root")
        return False
    
    print("\n📦 Checking current dependencies...")
    
    # Check if email-validator is in requirements
    with open("backend/requirements.txt", "r") as f:
        requirements = f.read()
    
    missing_deps = []
    
    if "email-validator" not in requirements:
        missing_deps.append("email-validator")
        print("   ❌ email-validator missing (required for EmailStr validation)")
    
    if "pydantic[email]" not in requirements and "email-validator" not in requirements:
        print("   ⚠️  Consider adding pydantic[email] for better email validation")
    
    # Check for other common missing dependencies
    common_deps = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "sqlalchemy": "Database ORM",
        "psycopg2-binary": "PostgreSQL adapter",
        "python-multipart": "File upload support",
        "python-jose": "JWT tokens",
        "passlib": "Password hashing",
        "Pillow": "Image processing"
    }
    
    for dep, description in common_deps.items():
        if dep not in requirements:
            missing_deps.append(dep)
            print(f"   ❌ {dep} missing ({description})")
    
    if missing_deps:
        print(f"\n🔧 Adding missing dependencies...")
        
        # Add email-validator if missing
        if "email-validator" in missing_deps:
            with open("backend/requirements.txt", "a") as f:
                f.write("\nemail-validator==2.1.0\n")
            print("   ✅ Added email-validator==2.1.0")
        
        print(f"\n📋 Missing dependencies added to requirements.txt")
        print("   Redeploy to Railway to apply changes")
    else:
        print("\n✅ All required dependencies are present!")
    
    print("\n🔍 Checking for potential issues...")
    
    # Check Python version compatibility
    python_version = sys.version_info
    print(f"   Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor >= 8:
        print("   ✅ Python version is compatible")
    else:
        print("   ⚠️  Consider using Python 3.8+ for better compatibility")
    
    # Check if requirements.txt is properly formatted
    lines = requirements.strip().split('\n')
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith('#') and '==' not in line and '>=' not in line and '<=' not in line:
            print(f"   ⚠️  Line {i}: Consider pinning version for '{line}'")
    
    print("\n🎯 Next Steps:")
    if missing_deps:
        print("1. ✅ Dependencies have been updated")
        print("2. 🔄 Redeploy to Railway")
        print("3. 🧪 Test the backend connection")
    else:
        print("1. ✅ Dependencies look good")
        print("2. 🔍 Check Railway logs for other issues")
        print("3. 🔄 Try restarting the Railway service")
    
    print("\n🌐 Test your backend after redeployment:")
    print("   curl -v https://art-app-production.up.railway.app/health")
    
    return True

if __name__ == "__main__":
    check_dependencies()
