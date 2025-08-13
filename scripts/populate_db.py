#!/usr/bin/env python3
"""
Populate database with sample artworks for testing
"""

from database.config import SessionLocal
from database.models import Artwork
from datetime import datetime

def populate_sample_artworks():
    """Initialize database with real API data instead of sample data"""
    db = SessionLocal()
    
    try:
        # Check if artworks already exist
        existing_count = db.query(Artwork).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} artworks. Skipping population.")
            return
        
        print("🔄 Database is empty. The application will fetch real artworks from APIs when needed.")
        print("💡 No sample data will be added - all artworks will come from live museum APIs.")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🎨 Populating database with sample artworks...")
    populate_sample_artworks() 