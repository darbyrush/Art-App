"""
Advanced Image Service for Art Explorer
Handles image optimization, caching, CDN, and fallback strategies
"""

import asyncio
import aiohttp
import hashlib
import os
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from fastapi import HTTPException
import json
from functools import lru_cache
import ssl

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - caching will be disabled")

class ImageService:
    def __init__(self):
        self.redis_client = None
        self.cache_ttl = 3600 * 24 * 7  # 7 days
        self.max_image_size = 1024 * 1024  # 1MB
        self.supported_formats = ['JPEG', 'PNG', 'WEBP']
        
        # Create SSL context - secure in production, lenient in development
        self.ssl_context = ssl.create_default_context()
        
        # In production, use strict SSL verification
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            # Use system default certificate verification
            pass
        else:
            # In development, allow self-signed certificates for testing
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=0,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Redis connected successfully")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not installed - running without caching")
    
    async def validate_image_url(self, url: str) -> Dict:
        """Validate if image URL is accessible and get metadata"""
        try:
            # Create connector with SSL bypass for art APIs
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.head(url) as response:
                    if response.status != 200:
                        return {
                            'valid': False,
                            'error': f'HTTP {response.status}',
                            'content_type': response.headers.get('content-type', ''),
                            'content_length': response.headers.get('content-length', 0)
                        }
                    
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', 0)
                    
                    # Check if it's actually an image
                    if not content_type.startswith('image/'):
                        return {
                            'valid': False,
                            'error': f'Not an image: {content_type}',
                            'content_type': content_type,
                            'content_length': content_length
                        }
                    
                    # Try to get actual image data to validate
                    async with session.get(url) as get_response:
                        if get_response.status != 200:
                            return {
                                'valid': False,
                                'error': f'GET failed: {get_response.status}',
                                'content_type': content_type,
                                'content_length': content_length
                            }
                        
                        image_data = await get_response.read()
                        
                        # Try to open with PIL to validate it's a real image
                        try:
                            img = Image.open(BytesIO(image_data))
                            width, height = img.size
                            format = img.format
                            
                            return {
                                'valid': True,
                                'width': width,
                                'height': height,
                                'format': format,
                                'content_type': content_type,
                                'size_bytes': len(image_data),
                                'url': url
                            }
                        except Exception as e:
                            return {
                                'valid': False,
                                'error': f'Invalid image format: {str(e)}',
                                'content_type': content_type,
                                'content_length': len(image_data)
                            }
                        
        except Exception as e:
            logger.warning(f"Image validation failed for {url}: {e}")
            return {
                'valid': False,
                'error': str(e),
                'url': url
            }
    
    async def download_and_validate_image(self, url: str) -> Optional[bytes]:
        """Download and validate image, return image data if valid"""
        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    image_data = await response.read()
                    
                    # Validate it's a real image
                    try:
                        img = Image.open(BytesIO(image_data))
                        img.verify()  # Verify the image
                        return image_data
                    except Exception as e:
                        logger.warning(f"Invalid image data from {url}: {e}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error downloading image {url}: {e}")
            return None
    
    async def optimize_image(
        self, 
        image_url: str, 
        width: int = 400, 
        height: int = 400,
        quality: int = 85,
        format: str = 'JPEG'
    ) -> Optional[bytes]:
        """Download and optimize image with caching"""
        
        # Check cache first
        cache_key = f"img:{hashlib.md5(f'{image_url}:{width}x{height}:{quality}'.encode()).hexdigest()}"
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return cached.encode('latin1')
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        try:
            # Download and validate image
            image_data = await self.download_and_validate_image(image_url)
            if not image_data:
                return None
            
            # Optimize image
            optimized = await self._process_image(
                image_data, width, height, quality, format
            )
            
            # Cache result
            if self.redis_client and optimized:
                try:
                    self.redis_client.setex(
                        cache_key, 
                        self.cache_ttl, 
                        optimized.decode('latin1')
                    )
                except Exception as e:
                    logger.warning(f"Redis cache write error: {e}")
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing image {image_url}: {e}")
            return None
    
    async def _process_image(
        self, 
        image_data: bytes, 
        width: int, 
        height: int, 
        quality: int, 
        format: str
    ) -> Optional[bytes]:
        """Process and optimize image"""
        try:
            # Open image
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize with aspect ratio preservation
            img = ImageOps.fit(img, (width, height), centering=(0.5, 0.5))
            
            # Optimize
            output = BytesIO()
            
            if format == 'WEBP':
                img.save(output, format='WEBP', quality=quality, method=6)
            elif format == 'PNG':
                img.save(output, format='PNG', optimize=True)
            else:  # JPEG
                img.save(output, format='JPEG', quality=quality, optimize=True)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def generate_placeholder(
        self, 
        source: str, 
        width: int = 400, 
        height: int = 400,
        style: str = 'modern'
    ) -> bytes:
        """Generate optimized placeholder image with caching"""
        
        cache_key = f"placeholder:{source}:{width}x{height}:{style}"
        
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return cached.encode('latin1')
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        try:
            # Create placeholder based on style
            if style == 'modern':
                img = self._create_modern_placeholder(source, width, height)
            elif style == 'minimal':
                img = self._create_minimal_placeholder(source, width, height)
            else:
                img = self._create_classic_placeholder(source, width, height)
            
            # Optimize
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            result = output.getvalue()
            
            # Cache result
            if self.redis_client:
                try:
                    self.redis_client.setex(cache_key, self.cache_ttl, result.decode('latin1'))
                except Exception as e:
                    logger.warning(f"Redis cache write error: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating placeholder for {source} with style {style}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_fallback_placeholder(width, height)
    
    def _create_modern_placeholder(self, source: str, width: int, height: int) -> Image.Image:
        """Create modern gradient placeholder"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            r = int(240 - (y / height) * 40)
            g = int(245 - (y / height) * 30)
            b = int(250 - (y / height) * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add text with robust font loading
        font = None
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 20)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        text = f"Artwork from {source.title()}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add text shadow
        draw.text((x+1, y+1), text, fill='#4a5568', font=font)
        draw.text((x, y), text, fill='#2d3748', font=font)
        
        return img
    
    def _create_minimal_placeholder(self, source: str, width: int, height: int) -> Image.Image:
        """Create minimal placeholder"""
        img = Image.new('RGB', (width, height), color='#f7fafc')
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([0, 0, width-1, height-1], outline='#e2e8f0', width=2)
        
        # Add icon
        icon_size = 48
        icon_x = (width - icon_size) // 2
        icon_y = (height - icon_size) // 2 - 20
        
        draw.rectangle([icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
                      fill='#cbd5e0', outline='#a0aec0')
        
        # Add text with robust font loading
        font = None
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 16)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        text = source.title()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        x = (width - text_width) // 2
        y = icon_y + icon_size + 10
        
        draw.text((x, y), text, fill='#718096', font=font)
        
        return img
    
    def _create_classic_placeholder(self, source: str, width: int, height: int) -> Image.Image:
        """Create classic placeholder (current implementation)"""
        img = Image.new('RGB', (width, height), color='#f3f4f6')
        draw = ImageDraw.Draw(img)
        
        # Add text with robust font loading
        font = None
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 24)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        text = f"Artwork\n{source.title()}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#6b7280', font=font)
        
        return img
    
    def _create_fallback_placeholder(self, width: int, height: int) -> bytes:
        """Create basic fallback placeholder"""
        img = Image.new('RGB', (width, height), color='#e5e7eb')
        output = BytesIO()
        img.save(output, format='JPEG', quality=70)
        output.seek(0)
        return output.getvalue()
    
    async def get_image_info(self, url: str) -> Dict:
        """Get image metadata"""
        return await self.validate_image_url(url)
    
    def clear_cache(self, pattern: str = None) -> int:
        """Clear image cache"""
        if not self.redis_client:
            return 0
        
        try:
            if pattern:
                keys = self.redis_client.keys(pattern)
            else:
                keys = self.redis_client.keys("img:*")
            
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

# Global instance
image_service = ImageService() 