#!/usr/bin/env python3
"""
Artwork Populator Service
Fetches artworks from external APIs and stores them in the database
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import SessionLocal
from database.models import Artwork, APICache
from backend.services.fetchers.random_art import fetch_artworks_from_sources
from backend.services.fetchers.cleveland import fetch_from_cleveland
from backend.services.fetchers.smithsonian import fetch_from_smithsonian
from backend.services.fetchers.met import fetch_from_met
from backend.services.fetchers.harvard import fetch_from_harvard
from backend.services.fetchers.national_gallery import fetch_from_national_gallery
from backend.services.fetchers.walters import fetch_from_walters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArtworkPopulator:
    """Service to populate database with artworks from external APIs"""
    
    def __init__(self):
        self.sources = {
            'cleveland': fetch_from_cleveland,
            'smithsonian': fetch_from_smithsonian,
            'met': fetch_from_met,
            'harvard': fetch_from_harvard,
            'national_gallery': fetch_from_national_gallery,
            'walters': fetch_from_walters
        }
    
    def get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def artwork_exists(self, db: Session, external_id: str, source: str) -> bool:
        """Check if artwork already exists in database"""
        return db.query(Artwork).filter(
            and_(Artwork.external_id == external_id, Artwork.source == source)
        ).first() is not None
    
    def save_artwork(self, db: Session, artwork_data: Dict) -> Optional[Artwork]:
        """Save artwork to database if it doesn't exist"""
        try:
            # Check if artwork already exists
            if self.artwork_exists(db, artwork_data.get('external_id', ''), artwork_data.get('source', '')):
                return None
            
            # Create new artwork
            artwork = Artwork(
                title=artwork_data.get('title', 'Untitled'),
                artist=artwork_data.get('artist'),
                date=artwork_data.get('date'),
                origin=artwork_data.get('origin'),
                department=artwork_data.get('department'),
                source=artwork_data.get('source'),
                image_url=artwork_data.get('image_url'),
                external_id=artwork_data.get('external_id')
            )
            
            db.add(artwork)
            db.commit()
            db.refresh(artwork)
            
            logger.info(f"Saved artwork: {artwork.title} from {artwork.source}")
            return artwork
            
        except Exception as e:
            logger.error(f"Error saving artwork: {e}")
            db.rollback()
            return None
    
    def fetch_and_save_from_source(self, source_name: str, fetch_func, limit: int = 10) -> int:
        """Fetch artworks from a specific source and save to database"""
        db = self.get_db()
        saved_count = 0
        
        try:
            logger.info(f"Fetching artworks from {source_name}...")
            
            # Fetch artworks from external API
            artworks = fetch_func(set())  # Pass empty set for seen_urls
            
            if not artworks:
                logger.warning(f"No artworks returned from {source_name}")
                return 0
            
            # Save each artwork
            for artwork_data in artworks:
                if self.save_artwork(db, artwork_data):
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} new artworks from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
        finally:
            db.close()
        
        return saved_count
    
    def populate_all_sources(self, artworks_per_source: int = 5) -> Dict[str, int]:
        """Populate database with artworks from all sources"""
        results = {}
        total_saved = 0
        
        logger.info(f"Starting database population with {artworks_per_source} artworks per source...")
        
        for source_name, fetch_func in self.sources.items():
            try:
                saved_count = self.fetch_and_save_from_source(source_name, fetch_func, artworks_per_source)
                results[source_name] = saved_count
                total_saved += saved_count
            except Exception as e:
                logger.error(f"Failed to populate from {source_name}: {e}")
                results[source_name] = 0
        
        logger.info(f"Database population complete. Total saved: {total_saved}")
        return results
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        db = self.get_db()
        try:
            total_artworks = db.query(Artwork).count()
            source_counts = {}
            
            for source_name in self.sources.keys():
                count = db.query(Artwork).filter(Artwork.source.ilike(f"%{source_name}%")).count()
                source_counts[source_name] = count
            
            return {
                'total_artworks': total_artworks,
                'source_counts': source_counts
            }
        finally:
            db.close()
    
    def cleanup_old_artworks(self, days_old: int = 30) -> int:
        """Remove old artworks from database (optional cleanup)"""
        db = self.get_db()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            old_artworks = db.query(Artwork).filter(Artwork.created_at < cutoff_date).all()
            
            for artwork in old_artworks:
                db.delete(artwork)
            
            db.commit()
            deleted_count = len(old_artworks)
            logger.info(f"Cleaned up {deleted_count} old artworks")
            return deleted_count
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

def populate_database(artworks_per_source: int = 5) -> Dict[str, int]:
    """Main function to populate database"""
    populator = ArtworkPopulator()
    return populator.populate_all_sources(artworks_per_source)

def get_stats() -> Dict:
    """Get database statistics"""
    populator = ArtworkPopulator()
    return populator.get_database_stats()

if __name__ == "__main__":
    # Test the populator
    print("🎨 Artwork Database Populator")
    print("=" * 40)
    
    # Get current stats
    stats = get_stats()
    print(f"Current database: {stats['total_artworks']} artworks")
    for source, count in stats['source_counts'].items():
        print(f"  {source}: {count}")
    
    # Populate database
    print("\n📥 Populating database...")
    results = populate_database(artworks_per_source=3)
    
    print("\n✅ Population Results:")
    for source, count in results.items():
        print(f"  {source}: {count} new artworks")
    
    # Get updated stats
    new_stats = get_stats()
    print(f"\n📊 Updated database: {new_stats['total_artworks']} artworks")
    for source, count in new_stats['source_counts'].items():
        print(f"  {source}: {count}") 