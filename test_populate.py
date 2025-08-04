#!/usr/bin/env python3
"""
Test script to populate database with real artwork data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.artwork_populator import populate_database, get_stats

def test_populate():
    """Test populating the database"""
    print("🎨 Testing database population...")
    print("=" * 50)
    
    # Get initial stats
    initial_stats = get_stats()
    print(f"Initial database: {initial_stats['total_artworks']} artworks")
    
    # Populate database
    print("\n🔄 Populating database...")
    try:
        results = populate_database(artworks_per_source=2)
        print("✅ Population results:")
        for source, count in results.items():
            print(f"  {source}: {count} artworks")
        
        # Get final stats
        final_stats = get_stats()
        print(f"\n📊 Final database: {final_stats['total_artworks']} artworks")
        
        if final_stats['total_artworks'] > 0:
            print("✅ Database populated successfully!")
            return True
        else:
            print("❌ No artworks were added to database")
            return False
            
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        return False

if __name__ == "__main__":
    test_populate() 