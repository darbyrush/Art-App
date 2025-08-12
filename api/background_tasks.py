#!/usr/bin/env python3
"""
Background tasks for continuous database population
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session

from database.config import SessionLocal
from database.models import Artwork
from artwork_populator import ArtworkPopulator

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for database maintenance"""
    
    def __init__(self):
        self.populator = ArtworkPopulator()
        self.last_population = datetime.utcnow()
        self.population_interval = timedelta(hours=6)  # Populate every 6 hours
    
    def should_populate_database(self) -> bool:
        """Check if database should be populated based on time and count"""
        db = SessionLocal()
        try:
            # Check if enough time has passed
            if datetime.utcnow() - self.last_population < self.population_interval:
                return False
            
            # Check current artwork count
            total_artworks = db.query(Artwork).count()
            
            # Populate if we have less than 200 artworks
            if total_artworks < 200:
                logger.info(f"Database has {total_artworks} artworks, triggering population")
                return True
            
            # Check source diversity
            source_counts = {}
            for source in self.populator.sources.keys():
                count = db.query(Artwork).filter(Artwork.source == source).count()
                source_counts[source] = count
            
            # Populate if any source has less than 20 artworks
            for source, count in source_counts.items():
                if count < 20:
                    logger.info(f"Source {source} has only {count} artworks, triggering population")
                    return True
            
            return False
            
        finally:
            db.close()
    
    def populate_database_background(self) -> Dict[str, int]:
        """Populate database with new artworks in background"""
        try:
            logger.info("Starting background database population...")
            
            # Get current stats
            db = SessionLocal()
            initial_count = db.query(Artwork).count()
            db.close()
            
            # Populate from all sources
            results = self.populator.populate_all_sources(artworks_per_source=5)
            
            # Update last population time
            self.last_population = datetime.utcnow()
            
            # Get final stats
            db = SessionLocal()
            final_count = db.query(Artwork).count()
            db.close()
            
            total_added = final_count - initial_count
            logger.info(f"Background population complete. Added {total_added} artworks")
            
            return {
                "results": results,
                "total_added": total_added,
                "timestamp": self.last_population.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in background population: {e}")
            return {"error": str(e)}
    
    def cleanup_old_artworks(self) -> int:
        """Remove old artworks to keep database size manageable"""
        try:
            db = SessionLocal()
            
            # Remove artworks older than 30 days that haven't been liked
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Get artworks to delete
            old_artworks = db.query(Artwork).filter(
                and_(
                    Artwork.created_at < cutoff_date,
                    ~Artwork.id.in_(
                        db.query(UserLike.artwork_id).filter(UserLike.liked == True)
                    )
                )
            ).all()
            
            deleted_count = len(old_artworks)
            
            # Delete old artworks
            for artwork in old_artworks:
                db.delete(artwork)
            
            db.commit()
            db.close()
            
            logger.info(f"Cleaned up {deleted_count} old artworks")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old artworks: {e}")
            return 0
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        db = SessionLocal()
        try:
            total_artworks = db.query(Artwork).count()
            
            # Source distribution
            source_counts = {}
            for source in self.populator.sources.keys():
                count = db.query(Artwork).filter(Artwork.source == source).count()
                source_counts[source] = count
            
            # Age distribution
            recent_artworks = db.query(Artwork).filter(
                Artwork.created_at >= datetime.utcnow() - timedelta(days=1)
            ).count()
            
            week_old_artworks = db.query(Artwork).filter(
                Artwork.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            return {
                "total_artworks": total_artworks,
                "source_distribution": source_counts,
                "recent_artworks": recent_artworks,
                "week_old_artworks": week_old_artworks,
                "last_population": self.last_population.isoformat(),
                "next_population": (self.last_population + self.population_interval).isoformat()
            }
            
        finally:
            db.close()

# Global background task manager
background_manager = BackgroundTaskManager()

def run_background_tasks():
    """Run all background tasks"""
    try:
        # Check if we should populate database
        if background_manager.should_populate_database():
            background_manager.populate_database_background()
        
        # Clean up old artworks (run less frequently)
        if datetime.utcnow().hour == 2:  # Run at 2 AM
            background_manager.cleanup_old_artworks()
            
    except Exception as e:
        logger.error(f"Error in background tasks: {e}")

# Import missing dependencies
from sqlalchemy import and_
from database.models import UserLike 