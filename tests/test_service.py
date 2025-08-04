#!/usr/bin/env python3
"""
Test UserService
"""

from database.config import SessionLocal
from api.services import UserService
from api.schemas import UserCreate

def test_user_service():
    """Test user service"""
    try:
        print("Testing UserService...")
        
        # Get database session
        db = SessionLocal()
        
        # Create service
        user_service = UserService()
        
        # Test user creation
        user_data = UserCreate(
            username="testuser3",
            password="testpass123",
            email="test3@example.com"
        )
        
        print(f"Creating user: {user_data.username}")
        result = user_service.create_user(db, user_data)
        print(f"✅ User created: {result.username}")
        
        return True
    except Exception as e:
        print(f"❌ UserService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_service() 