"""
Comprehensive caching service for Art Explorer API
Optimized for scaling to 50+ concurrent users
"""

import redis
import json
import pickle
import hashlib
import logging
from typing import Any, Optional, Union, Dict, List
from functools import wraps
import time
import os

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service with multiple caching strategies"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        self._fallback_cache = {}  # In-memory fallback cache
        self._fallback_ttl = {}    # TTL for fallback cache
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            # Get Redis configuration from environment
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            # Skip Redis if host is localhost in production (Railway)
            if redis_host == 'localhost' and os.getenv('ENVIRONMENT') == 'production':
                logger.info("🚫 Redis disabled in production (localhost not available)")
                self.enabled = False
                self.redis_client = None
                return
            
            # Create Redis client
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=False,  # Keep as bytes for pickle
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=50  # Scale for 50 users
            )
            
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"✅ Redis cache connected: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache disabled: {e}")
            self.enabled = False
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        # Create a hash of the arguments
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.enabled and self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)
                return None
            except Exception as e:
                logger.warning(f"Redis get error for key {key}: {e}")
                # Fall back to in-memory cache
        
        # Use fallback in-memory cache
        if key in self._fallback_cache:
            # Check TTL
            if time.time() < self._fallback_ttl.get(key, 0):
                return self._fallback_cache[key]
            else:
                # Expired, remove it
                del self._fallback_cache[key]
                del self._fallback_ttl[key]
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        if self.enabled and self.redis_client:
            try:
                data = pickle.dumps(value)
                result = self.redis_client.setex(key, expire, data)
                if result:
                    return True
            except Exception as e:
                logger.warning(f"Redis set error for key {key}: {e}")
        
        # Fallback to in-memory cache
        try:
            self._fallback_cache[key] = value
            self._fallback_ttl[key] = time.time() + expire
            # Clean up expired keys
            self._cleanup_fallback_cache()
            return True
        except Exception as e:
            logger.warning(f"Fallback cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        success = False
        
        if self.enabled and self.redis_client:
            try:
                success = bool(self.redis_client.delete(key))
            except Exception as e:
                logger.warning(f"Redis delete error for key {key}: {e}")
        
        # Also delete from fallback cache
        if key in self._fallback_cache:
            del self._fallback_cache[key]
            if key in self._fallback_ttl:
                del self._fallback_ttl[key]
            success = True
            
        return success
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.warning(f"Cache increment error for key {key}: {e}")
            return None
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.warning(f"Cache expire error for key {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache data"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.info("✅ Cache cleared successfully")
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False

    def _cleanup_fallback_cache(self):
        """Clean up expired keys from fallback cache"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._fallback_ttl.items() 
            if current_time > expiry
        ]
        for key in expired_keys:
            if key in self._fallback_cache:
                del self._fallback_cache[key]
            if key in self._fallback_ttl:
                del self._fallback_ttl[key]

# Global cache instance
cache_service = CacheService()

# Decorator for caching function results
def cache_result(prefix: str, expire: int = 3600, key_generator: Optional[callable] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_service.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_generator:
                cache_key = key_generator(prefix, *args, **kwargs)
            else:
                cache_key = cache_service._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, expire)
            logger.debug(f"Cache miss for {cache_key}, stored result")
            
            return result
        return wrapper
    return decorator

# Specific cache decorators for common use cases
def cache_artwork(expire: int = 1800):  # 30 minutes for artwork data
    """Cache artwork-related data"""
    return cache_result("artwork", expire)

def cache_user(expire: int = 3600):  # 1 hour for user data
    """Cache user-related data"""
    return cache_result("user", expire)

def cache_board(expire: int = 1800):  # 30 minutes for board data
    """Cache board-related data"""
    return cache_result("board", expire)

def cache_search(expire: int = 900):  # 15 minutes for search results
    """Cache search results"""
    return cache_result("search", expire)

# Rate limiting with Redis
class RateLimiter:
    """Rate limiting service using Redis"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed within rate limit window"""
        if not self.cache.enabled:
            return True
        
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"
        
        try:
            current_count = self.cache.get(window_key) or 0
            if current_count >= max_requests:
                return False
            
            # Increment counter
            self.cache.increment(window_key, 1)
            # Set expiration for the window
            self.cache.expire(window_key, window_seconds)
            
            return True
        except Exception as e:
            logger.warning(f"Rate limiting error: {e}")
            return True  # Allow if rate limiting fails
    
    def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests allowed"""
        if not self.cache.enabled:
            return max_requests
        
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"
        
        try:
            current_count = self.cache.get(window_key) or 0
            return max(0, max_requests - current_count)
        except Exception as e:
            logger.warning(f"Rate limit check error: {e}")
            return max_requests

# Global rate limiter instance
rate_limiter = RateLimiter(cache_service)

# Cache statistics
def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    if not cache_service.enabled or not cache_service.redis_client:
        return {"enabled": False}
    
    try:
        info = cache_service.redis_client.info()
        return {
            "enabled": True,
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
    except Exception as e:
        logger.warning(f"Cache stats error: {e}")
        return {"enabled": True, "error": str(e)}
