#!/usr/bin/env python3
"""
Image Validation and Caching Script
Validates all artwork images and caches the results in the database
"""

import sys
import os
import asyncio
import logging
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_db
from database.models import Artwork, ImageCache
from api.image_service import image_service
from api.services import image_cache_service
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def validate_artwork_images():
    """Validate all artwork images and cache results"""
    logger.info("Starting image validation process...")
    
    # Initialize database
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all artworks with image URLs
        artworks = db.query(Artwork).filter(Artwork.image_url.isnot(None)).all()
        logger.info(f"Found {len(artworks)} artworks with image URLs")
        
        if not artworks:
            logger.warning("No artworks with image URLs found")
            return
        
        # Group by source for better organization
        by_source = {}
        for artwork in artworks:
            source = artwork.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(artwork)
        
        total_valid = 0
        total_invalid = 0
        
        for source, source_artworks in by_source.items():
            logger.info(f"Processing {len(source_artworks)} artworks from {source}")
            
            # Get unique URLs for this source
            urls = list(set([artwork.image_url for artwork in source_artworks if artwork.image_url]))
            
            # Validate URLs in batches
            batch_size = 10
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                logger.info(f"Validating batch {i//batch_size + 1} ({len(batch_urls)} URLs)")
                
                for url in batch_urls:
                    try:
                        # Check if already cached
                        cached = image_cache_service.get_cached_image(db, url)
                        if cached and (datetime.utcnow() - cached.last_validated).days < 7:
                            logger.info(f"Using cached result for {url}")
                            if cached.is_valid:
                                total_valid += 1
                            else:
                                total_invalid += 1
                            continue
                        
                        # Validate image
                        logger.info(f"Validating {url}")
                        validation_result = await image_service.validate_image_url(url)
                        validation_result['source'] = source
                        validation_result['url'] = url
                        
                        # Cache result
                        image_cache_service.cache_image(db, validation_result)
                        
                        if validation_result.get('valid', False):
                            total_valid += 1
                            logger.info(f"✅ Valid: {url}")
                        else:
                            total_invalid += 1
                            logger.warning(f"❌ Invalid: {url} - {validation_result.get('error', 'Unknown error')}")
                        
                        # Small delay to be respectful to external APIs
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error validating {url}: {e}")
                        total_invalid += 1
        
        # Print summary
        logger.info("=" * 50)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total URLs processed: {total_valid + total_invalid}")
        logger.info(f"Valid images: {total_valid}")
        logger.info(f"Invalid images: {total_invalid}")
        logger.info(f"Success rate: {(total_valid / (total_valid + total_invalid) * 100):.1f}%")
        
        # Print breakdown by source
        logger.info("\nBREAKDOWN BY SOURCE:")
        for source in by_source.keys():
            valid_count = db.query(ImageCache).filter(
                ImageCache.source == source,
                ImageCache.is_valid == True
            ).count()
            total_count = db.query(ImageCache).filter(ImageCache.source == source).count()
            if total_count > 0:
                success_rate = (valid_count / total_count * 100)
                logger.info(f"{source}: {valid_count}/{total_count} ({success_rate:.1f}%)")
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error during validation: {e}")
        raise
    finally:
        db.close()

async def cleanup_old_cache():
    """Clean up old cache entries"""
    logger.info("Cleaning up old cache entries...")
    
    init_db()
    db = next(get_db())
    
    try:
        deleted = image_cache_service.cleanup_old_cache(db, days=30)
        logger.info(f"Cleaned up {deleted} old cache entries")
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
    finally:
        db.close()

async def get_cache_stats():
    """Get cache statistics"""
    logger.info("Getting cache statistics...")
    
    init_db()
    db = next(get_db())
    
    try:
        total_cached = db.query(ImageCache).count()
        valid_images = db.query(ImageCache).filter(ImageCache.is_valid == True).count()
        invalid_images = db.query(ImageCache).filter(ImageCache.is_valid == False).count()
        
        logger.info("=" * 50)
        logger.info("CACHE STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total cached: {total_cached}")
        logger.info(f"Valid images: {valid_images}")
        logger.info(f"Invalid images: {invalid_images}")
        if total_cached > 0:
            success_rate = (valid_images / total_cached * 100)
            logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Group by source
        from sqlalchemy import func
        sources = db.query(ImageCache.source, func.count(ImageCache.id)).group_by(ImageCache.source).all()
        logger.info("\nBY SOURCE:")
        for source, count in sources:
            valid_count = db.query(ImageCache).filter(
                ImageCache.source == source,
                ImageCache.is_valid == True
            ).count()
            success_rate = (valid_count / count * 100) if count > 0 else 0
            logger.info(f"{source}: {valid_count}/{count} ({success_rate:.1f}%)")
        
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Image validation and caching")
    parser.add_argument("--validate", action="store_true", help="Validate all artwork images")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old cache entries")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    
    args = parser.parse_args()
    
    if args.validate:
        asyncio.run(validate_artwork_images())
    elif args.cleanup:
        asyncio.run(cleanup_old_cache())
    elif args.stats:
        asyncio.run(get_cache_stats())
    else:
        # Default: validate images
        asyncio.run(validate_artwork_images()) 