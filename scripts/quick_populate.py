#!/usr/bin/env python3
"""
Quick database population script for testing
Fetches a smaller number of artworks quickly for development/testing
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import SessionLocal, init_db
from database.models import Artwork
from backend.registry import SOURCES
from backend.services.fetchers.random_art import fetch_artworks_from_sources

def quick_populate(target_count: int = 100):
    """Quick population with a smaller target count"""
    print(f"🚀 Quick database population - Target: {target_count} artworks")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    db = SessionLocal()
    
    try:
        # Check existing artworks
        existing_count = db.query(Artwork).count()
        print(f"📈 Current artworks: {existing_count}")
        
        if existing_count >= target_count:
            print(f"✅ Already have {existing_count} artworks")
            return
        
        # Get available sources
        available_sources = list(SOURCES.keys())
        print(f"🔍 Sources: {', '.join(available_sources)}")
        
        # Calculate per source (aim for diversity)
        per_source = max(1, (target_count - existing_count) // len(available_sources))
        print(f"📊 Fetching {per_source} per source...")
        
        total_fetched = 0
        seen_urls = set()
        
        for source_name in available_sources:
            print(f"\n🔄 {source_name}...")
            
            try:
                artworks = fetch_artworks_from_sources(
                    seen_urls=seen_urls,
                    selected_sources=[source_name],
                    max_per_source=per_source
                )
                
                if artworks:
                    source_fetched = 0
                    for artwork_data in artworks:
                        if not artwork_data.get('image_url'):
                            continue
                        
                        # Add source info
                        artwork_data['source'] = source_name
                        
                        # Check for duplicates
                        existing = db.query(Artwork).filter(
                            Artwork.image_url == artwork_data['image_url']
                        ).first()
                        
                        if not existing:
                            # Create artwork
                            db_artwork = Artwork(
                                title=artwork_data.get('title', 'Untitled'),
                                artist=artwork_data.get('artist', 'Unknown Artist'),
                                date=artwork_data.get('date', 'Unknown Date'),
                                origin=artwork_data.get('origin', 'Unknown Origin'),
                                department=artwork_data.get('department', 'Unknown Department'),
                                source=source_name,
                                image_url=artwork_data['image_url'],
                                external_id=artwork_data.get('external_id'),
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            
                            db.add(db_artwork)
                            source_fetched += 1
                            total_fetched += 1
                            seen_urls.add(artwork_data['image_url'])
                    
                    db.commit()
                    print(f"   ✅ {source_fetched} artworks added")
                    
                    if total_fetched >= target_count:
                        break
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Final summary
        final_count = db.query(Artwork).count()
        print(f"\n🎉 Quick population complete!")
        print(f"📊 Total artworks: {final_count}")
        print(f"🆕 New artworks: {total_fetched}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Quick Art Database Population")
    print("=" * 40)
    
    # Get target count from command line or use default
    target_count = 100
    if len(sys.argv) > 1:
        try:
            target_count = int(sys.argv[1])
        except ValueError:
            print("⚠️ Invalid target count, using default: 100")
    
    print(f"🎯 Target: {target_count} artworks")
    print()
    
    # Start population
    start_time = time.time()
    quick_populate(target_count)
    end_time = time.time()
    
    print(f"\n⏱️ Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
