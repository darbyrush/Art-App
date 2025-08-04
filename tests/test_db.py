#!/usr/bin/env python3
"""
Test database connection
"""

from database.config import engine
from sqlalchemy import text

def test_db_connection():
    """Test database connection"""
    try:
        print("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_db_connection() 