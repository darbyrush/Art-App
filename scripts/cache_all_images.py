#!/usr/bin/env python3
"""
Script to cache all artwork images in the database
This will download and store all images locally for faster access
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_db
from database.models import Artwork
from api.image_cache_service import image_cache_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cache_all_images():
    """Cache all artwork images in the database"""
    try:
        # Initialize database
        init_db()
        db = next(get_db())
        
        # Check if we're in the right directory
        import os
        if not os.path.exists('art_explorer.db'):
            print("Database not found in current directory")
            return {
                "total": 0,
                "cached": 0,
                "failed": 0
            }
        
        # Get all artworks with image URLs
        artworks = db.query(Artwork).filter(Artwork.image_url.isnot(None)).all()
        
        logger.info(f"Found {len(artworks)} artworks with image URLs")
        
        cached_count = 0
        failed_count = 0
        
        for i, artwork in enumerate(artworks, 1):
            try:
                logger.info(f"Processing {i}/{len(artworks)}: {artwork.title}")
                
                cached_image = await image_cache_service.get_or_download_image(
                    artwork.image_url, db, artwork.source
                )
                
                if cached_image and cached_image.is_valid:
                    cached_count += 1
                    logger.info(f"✅ Cached: {artwork.title}")
                else:
                    failed_count += 1
                    logger.warning(f"❌ Failed: {artwork.title}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error caching {artwork.title}: {e}")
        
        logger.info(f"\n=== Caching Complete ===")
        logger.info(f"Total artworks: {len(artworks)}")
        logger.info(f"Successfully cached: {cached_count}")
        logger.info(f"Failed: {failed_count}")
        
        return {
            "total": len(artworks),
            "cached": cached_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in cache_all_images: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting image caching process...")
    result = asyncio.run(cache_all_images())
    print(f"\nCaching completed!")
    print(f"Total: {result['total']}")
    print(f"Cached: {result['cached']}")
    print(f"Failed: {result['failed']}")
