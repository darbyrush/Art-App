import json
import os
import time
from functools import lru_cache
import requests
from typing import Dict, List, Set, Optional

SEEN_FILE = "seen_urls.json"
CACHE_DURATION = 300  # 5 minutes cache

# Simple in-memory cache
_cache = {}
_cache_timestamps = {}

# Performance tracking
_performance_stats = {
    "cache_hits": 0,
    "cache_misses": 0,
    "fetch_times": [],
    "total_requests": 0
}

def load_seen_urls() -> set[str]:
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    return set()

def save_feedback(art, liked: bool):
    seen = load_seen_urls()
    seen.add(art["image_url"])
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def standardize_artwork(title, artist, image_url, source, object_id=None, date=None, department=None):
    return {
        "title": title,
        "artist": artist,
        "image_url": image_url,
        "source": source,
        "object_id": object_id,
        "date": date,
        "department": department,
    }

def get_cached_data(key: str) -> Optional[Dict]:
    """Get cached data if it's still valid"""
    if key in _cache and key in _cache_timestamps:
        if time.time() - _cache_timestamps[key] < CACHE_DURATION:
            _performance_stats["cache_hits"] += 1
            return _cache[key]
        else:
            # Remove expired cache
            del _cache[key]
            del _cache_timestamps[key]
    _performance_stats["cache_misses"] += 1
    return None

def set_cached_data(key: str, data: Dict):
    """Cache data with timestamp"""
    _cache[key] = data
    _cache_timestamps[key] = time.time()

def clear_cache():
    """Clear all cached data"""
    global _cache, _cache_timestamps
    _cache.clear()
    _cache_timestamps.clear()

def fetch_with_retry(url: str, params: Dict = None, max_retries: int = 3, timeout: int = 10) -> Optional[requests.Response]:
    """Fetch data with retry logic and timeout"""
    start_time = time.time()
    _performance_stats["total_requests"] += 1
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                fetch_time = time.time() - start_time
                _performance_stats["fetch_times"].append(fetch_time)
                return response
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                print(f"HTTP {response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return None

def get_performance_stats() -> Dict:
    """Get performance statistics"""
    cache_hit_rate = 0
    if _performance_stats["cache_hits"] + _performance_stats["cache_misses"] > 0:
        cache_hit_rate = _performance_stats["cache_hits"] / (_performance_stats["cache_hits"] + _performance_stats["cache_misses"])
    
    avg_fetch_time = 0
    if _performance_stats["fetch_times"]:
        avg_fetch_time = sum(_performance_stats["fetch_times"]) / len(_performance_stats["fetch_times"])
    
    return {
        "cache_hits": _performance_stats["cache_hits"],
        "cache_misses": _performance_stats["cache_misses"],
        "cache_hit_rate": f"{cache_hit_rate:.2%}",
        "total_requests": _performance_stats["total_requests"],
        "avg_fetch_time": f"{avg_fetch_time:.2f}s",
        "cache_size": len(_cache)
    }

def reset_performance_stats():
    """Reset performance statistics"""
    global _performance_stats
    _performance_stats = {
        "cache_hits": 0,
        "cache_misses": 0,
        "fetch_times": [],
        "total_requests": 0
    }