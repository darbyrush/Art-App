"""
Simple in-memory cache for frequently accessed data
"""

import time
from typing import Any, Optional, Dict
from functools import wraps
import hashlib
import json

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create a cache key from arguments"""
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None
            
        entry = self._cache[key]
        if time.time() > entry['expires']:
            del self._cache[key]
            return None
            
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cache_result(self, ttl: Optional[int] = None):
        """Decorator to cache function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Skip caching for database sessions (first arg is usually db)
                cache_args = args[1:] if args and hasattr(args[0], 'query') else args
                cache_key = f"{func.__name__}_{self._make_key(*cache_args, **kwargs)}"
                
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator

# Global cache instance
app_cache = SimpleCache(default_ttl=300)  # 5 minutes

def cache_user_by_username(ttl: int = 600):
    """Cache user lookups by username for 10 minutes"""
    return app_cache.cache_result(ttl)

def cache_artwork_by_id(ttl: int = 1800):
    """Cache artwork lookups by ID for 30 minutes"""
    return app_cache.cache_result(ttl)

def invalidate_user_cache(username: str):
    """Invalidate cached user data"""
    # This is a simple implementation - in production you'd want more sophisticated invalidation
    app_cache.clear()

def invalidate_artwork_cache(artwork_id: str):
    """Invalidate cached artwork data"""
    app_cache.clear()
