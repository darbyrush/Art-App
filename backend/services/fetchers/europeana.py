import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data
from backend.config import config

BASE_URL = "https://api.europeana.eu/record/v2/search.json"

def fetch_from_europeana(seen_urls: set[str] = set()):
    # Get API key from configuration
    api_key = config.europeana_api_key
    if not api_key:
        print("[europeana] Warning: No API key found. Set EUROPEANA_API_KEY environment variable.")
        return []
    
    results = []
    try:
        # Europeana API parameters
        params = {
            "wskey": api_key,
            "query": "art",
            "media": True,
            "rows": 20,
            "start": random.randint(0, 100),
            "profile": "rich"
        }
        
        # Check cache first
        cache_key = f"europeana_start_{params['start']}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print(f"[europeana] Using cached data for start={params['start']}")
            data = cached_data
        else:
            # Fetch fresh data
            response = fetch_with_retry(BASE_URL, params=params)
            if not response or not response.ok:
                print(f"[europeana] Request failed with status {response.status_code if response else 'No response'}")
                return results
                
            data = response.json()
            set_cached_data(cache_key, data)
        
        # Process results
        for item in data.get("items", []):
            # Extract image URL
            image_url = None
            if item.get("edmIsShownBy"):
                image_url = item["edmIsShownBy"][0]
            elif item.get("edmIsShownAt"):
                image_url = item["edmIsShownAt"][0]
            
            if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue
            
            # Extract title
            title = "Unknown"
            if item.get("title"):
                title = item["title"][0] if isinstance(item["title"], list) else item["title"]
            
            # Extract artist
            artist = "Unknown"
            if item.get("dcCreator"):
                artist = item["dcCreator"][0] if isinstance(item["dcCreator"], list) else item["dcCreator"]
            
            # Extract date
            date = "Unknown"
            if item.get("year"):
                date = str(item["year"])
            elif item.get("edmTimespanLabel"):
                date = item["edmTimespanLabel"][0] if isinstance(item["edmTimespanLabel"], list) else item["edmTimespanLabel"]
            
            # Extract origin
            origin = "Unknown"
            if item.get("country"):
                origin = item["country"][0] if isinstance(item["country"], list) else item["country"]
            
            results.append({
                "title": title,
                "artist": artist,
                "date": date,
                "origin": origin,
                "department": "European Cultural Heritage",
                "image_url": image_url,
                "source": "Europeana"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[europeana] Error: {e}")

    print(f"[europeana] Returning {len(results)} artworks")
    return results 