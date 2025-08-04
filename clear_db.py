#!/usr/bin/env python3
"""
Clear database to remove sample data with broken image URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.config import SessionLocal
from database.models import Artwork, User, UserLike, UserRating, UserNote, APICache

def clear_database():
    """Clear all data from database"""
    db = SessionLocal()
    
    try:
        print("🗑️ Clearing database...")
        
        # Delete all data
        db.query(APICache).delete()
        db.query(UserNote).delete()
        db.query(UserRating).delete()
        db.query(UserLike).delete()
        db.query(Artwork).delete()
        db.query(User).delete()
        
        db.commit()
        print("✅ Database cleared successfully!")
        print("🔄 The application will now fetch fresh data from live APIs.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_database() 