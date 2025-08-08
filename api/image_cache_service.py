import aiohttp
import ssl
import base64
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import ImageCache
from database.config import get_db
import logging

logger = logging.getLogger(__name__)

class ImageCacheService:
    def __init__(self):
        self.session = None
    
    async def get_cached_image(self, url: str, db: Session) -> ImageCache:
        """Get cached image from database"""
        return db.query(ImageCache).filter(ImageCache.original_url == url).first()
    
    async def download_and_cache_image(self, url: str, db: Session, source: str = None) -> ImageCache:
        """Download image and cache it in database"""
        try:
            # Check if already cached
            cached = await self.get_cached_image(url, db)
            if cached and cached.is_valid:
                return cached
            
            # Create SSL context that ignores certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create connector with SSL context
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            # Download image
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        content = await response.read()
                        content_type = response.headers.get('content-type', 'image/jpeg')
                        
                        # Encode as base64
                        image_data = base64.b64encode(content).decode('utf-8')
                        
                        # Create or update cache entry
                        if cached:
                            cached.image_data = image_data
                            cached.is_valid = True
                            cached.size_bytes = len(content)
                            cached.format = content_type.split('/')[-1] if '/' in content_type else 'jpeg'
                            cached.last_validated = datetime.utcnow()
                            cached.error_message = None
                        else:
                            cached = ImageCache(
                                original_url=url,
                                image_data=image_data,
                                is_valid=True,
                                size_bytes=len(content),
                                format=content_type.split('/')[-1] if '/' in content_type else 'jpeg',
                                source=source,
                                last_validated=datetime.utcnow()
                            )
                            db.add(cached)
                        
                        db.commit()
                        logger.info(f"Successfully cached image: {url}")
                        return cached
                    else:
                        # Cache the error
                        if cached:
                            cached.is_valid = False
                            cached.error_message = f"HTTP {response.status}"
                            cached.last_validated = datetime.utcnow()
                        else:
                            cached = ImageCache(
                                original_url=url,
                                is_valid=False,
                                error_message=f"HTTP {response.status}",
                                source=source,
                                last_validated=datetime.utcnow()
                            )
                            db.add(cached)
                        
                        db.commit()
                        logger.warning(f"Failed to download image: {url} - HTTP {response.status}")
                        return cached
                        
        except Exception as e:
            # Cache the error
            if cached:
                cached.is_valid = False
                cached.error_message = str(e)
                cached.last_validated = datetime.utcnow()
            else:
                cached = ImageCache(
                    original_url=url,
                    is_valid=False,
                    error_message=str(e),
                    source=source,
                    last_validated=datetime.utcnow()
                )
                db.add(cached)
            
            db.commit()
            logger.error(f"Error downloading image {url}: {e}")
            return cached
    
    async def get_or_download_image(self, url: str, db: Session, source: str = None) -> ImageCache:
        """Get cached image or download and cache it"""
        cached = await self.get_cached_image(url, db)
        
        if cached and cached.is_valid:
            return cached
        
        # Download and cache
        return await self.download_and_cache_image(url, db, source)
    
    def get_image_data_url(self, image_cache: ImageCache) -> str:
        """Convert cached image data to data URL"""
        if not image_cache or not image_cache.is_valid or not image_cache.image_data:
            return None
        
        format_type = image_cache.format or 'jpeg'
        return f"data:image/{format_type};base64,{image_cache.image_data}"

# Global instance
image_cache_service = ImageCacheService()
