import requests
from backend.utils import standardize_artwork, fetch_with_retry, get_cached_data, set_cached_data
from backend.config import config

BASE_URL = "https://api.harvardartmuseums.org/object"

def fetch_from_harvard(seen_urls: set[str] = set()):
    # Get API key from configuration
    api_key = config.harvard_api_key
    if not api_key:
        print("[harvard] Warning: No API key found. Set HARVARD_API_KEY environment variable.")
        return []
    
    params = {
        "apikey": api_key,
        "hasimage": 1,
        "size": 50
    }
    
    # Check cache first
    cache_key = f"harvard_search_{hash(str(params))}"
    cached_data = get_cached_data(cache_key)
    
    if cached_data:
        print("[harvard] Using cached data")
        data = cached_data
    else:
        # Fetch fresh data
        response = fetch_with_retry(BASE_URL, params=params)
        if not response or not response.ok:
            print(f"[harvard] Request failed with status {response.status_code if response else 'No response'}")
            return []
            
        data = response.json()
        set_cached_data(cache_key, data)

    artworks = []
    for item in data.get("records", []):
        image_url = item.get("primaryimageurl")
        if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
            continue
            
        # Extract artist information
        artist = "Unknown"
        people = item.get("people", [])
        if people and len(people) > 0:
            artist = people[0].get("name", "Unknown")
        
        artworks.append(standardize_artwork(
            title=item.get("title", "Unknown"),
            artist=artist,
            image_url=image_url,
            source="Harvard Art Museums"
        ))
        
        # Limit results
        if len(artworks) >= 5:
            break
    
    print(f"[harvard] Returning {len(artworks)} artworks")
    return artworks