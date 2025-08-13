#!/usr/bin/env python3
"""
Simple database connection test script
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing imports...")
    
    # Test database models import
    print("1. Testing database models import...")
    from api.database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
    print("   ✅ Database models imported successfully")
    
    # Test database config import
    print("2. Testing database config import...")
    from api.database.config import get_db, init_db, test_connection
    print("   ✅ Database config imported successfully")
    
    # Test schemas import
    print("3. Testing schemas import...")
    from api.schemas import UserCreate, UserResponse, UserUpdate
    print("   ✅ Schemas imported successfully")
    
    # Test services import
    print("4. Testing services import...")
    from api.services import UserService
    print("   ✅ Services imported successfully")
    
    # Test auth import
    print("5. Testing auth import...")
    from api.auth import get_current_user, create_access_token, get_password_hash
    print("   ✅ Auth imported successfully")
    
    print("\n✅ All imports successful!")
    
    # Test database connection
    print("\nTesting database connection...")
    try:
        init_db()
        print("   ✅ Database initialized successfully")
        
        if test_connection():
            print("   ✅ Database connection test passed")
        else:
            print("   ❌ Database connection test failed")
            
    except Exception as e:
        print(f"   ❌ Database connection error: {e}")
        print(f"   Error type: {type(e)}")
    
    # Test creating a user
    print("\nTesting user creation...")
    try:
        from sqlalchemy.orm import Session
        from api.database.config import get_db
        
        # Get a database session
        db = next(get_db())
        
        # Test UserService
        user_service = UserService()
        
        # Test creating a user
        test_user = UserCreate(username="testuser", password="testpass123")
        
        # Check if user exists
        existing_user = user_service.get_user_by_username(db, username=test_user.username)
        if existing_user:
            print("   ✅ User service working - user exists check passed")
        else:
            print("   ✅ User service working - no existing user found")
            
        db.close()
        
    except Exception as e:
        print(f"   ❌ User creation test error: {e}")
        print(f"   Error type: {type(e)}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"❌ Import error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
