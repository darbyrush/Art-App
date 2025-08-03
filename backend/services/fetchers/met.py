import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def fetch_from_met(seen_urls: set[str] = set()):
    results = []
    try:
        # MET API doesn't support search with GET, so we'll use random object IDs
        # but with a smarter approach - use known ranges
        object_ranges = [
            (1, 100000),      # Early objects
            (100000, 200000), # 19th century
            (200000, 300000), # Modern
            (300000, 400000), # Contemporary
            (400000, 500000), # Various periods
        ]
        
        # Pick a random range
        start_range, end_range = random.choice(object_ranges)
        
        # Try multiple random IDs from this range
        attempts = 0
        max_attempts = 20
        
        while len(results) < 5 and attempts < max_attempts:
            object_id = random.randint(start_range, end_range)
            attempts += 1
            
            # Check cache first
            cache_key = f"met_object_{object_id}"
            cached_data = get_cached_data(cache_key)
            
            if cached_data:
                data = cached_data
            else:
                # Fetch object details
                resp = fetch_with_retry(f"{BASE_URL}/objects/{object_id}")
                if not resp or not resp.ok:
                    continue
                    
                data = resp.json()
                set_cached_data(cache_key, data)
            
            # Extract image URL
            image_url = data.get("primaryImageSmall") or data.get("primaryImage")
            if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue

            # Check if object has basic required info
            title = data.get("title")
            if not title:
                continue

            results.append({
                "title": title,
                "artist": data.get("artistDisplayName", "Unknown"),
                "date": data.get("objectDate", "Unknown"),
                "origin": data.get("culture") or data.get("country", "Unknown"),
                "department": data.get("department", "Unknown"),
                "image_url": image_url,
                "source": "Metropolitan Museum of Art"
            })
                
    except Exception as e:
        print(f"[met] Error: {e}")

    print(f"[met] Returning {len(results)} artworks")
    return results