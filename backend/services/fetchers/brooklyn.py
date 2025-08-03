import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://www.brooklynmuseum.org/api/v2/object"

def fetch_from_brooklyn(seen_urls: set[str] = set()):
    results = []
    try:
        # Brooklyn Museum API parameters
        params = {
            "limit": 20,
            "offset": random.randint(0, 1000),
            "has_image": True
        }
        
        # Check cache first
        cache_key = f"brooklyn_offset_{params['offset']}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print(f"[brooklyn] Using cached data for offset {params['offset']}")
            data = cached_data
        else:
            # Fetch fresh data
            response = fetch_with_retry(BASE_URL, params=params)
            if not response or not response.ok:
                print(f"[brooklyn] Request failed with status {response.status_code if response else 'No response'}")
                return results
                
            data = response.json()
            set_cached_data(cache_key, data)
        
        # Process results
        for item in data.get("data", []):
            # Extract image URL
            image_url = None
            if item.get("images") and len(item["images"]) > 0:
                image_url = item["images"][0].get("url")
            
            if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue
            
            # Extract artist information
            artist = "Unknown"
            if item.get("artists") and len(item["artists"]) > 0:
                artist = item["artists"][0].get("name", "Unknown")
            
            # Extract date information
            date = "Unknown"
            if item.get("date"):
                date = item["date"].get("display_date", "Unknown")
            
            results.append({
                "title": item.get("title", "Unknown"),
                "artist": artist,
                "date": date,
                "origin": item.get("culture", "Unknown"),
                "department": item.get("department", "Unknown"),
                "image_url": image_url,
                "source": "Brooklyn Museum"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[brooklyn] Error: {e}")

    print(f"[brooklyn] Returning {len(results)} artworks")
    return results 