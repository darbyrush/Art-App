import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://www.rijksmuseum.nl/api/en/collection"

def fetch_from_rijks(seen_urls: set[str] = set()):
    results = []
    try:
        # Rijksmuseum API parameters - no API key needed for basic access
        params = {
            "format": "json",
            "imgonly": True,
            "ps": 20,  # page size
            "p": random.randint(1, 50)  # page number
        }
        
        # Check cache first
        cache_key = f"rijks_page_{params['p']}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print(f"[rijks] Using cached data for page {params['p']}")
            data = cached_data
        else:
            # Fetch fresh data
            response = fetch_with_retry(BASE_URL, params=params)
            if not response or not response.ok:
                print(f"[rijks] Request failed with status {response.status_code if response else 'No response'}")
                return results
                
            data = response.json()
            set_cached_data(cache_key, data)
        
        # Process results
        for item in data.get("artObjects", []):
            # Extract image URL
            image_url = None
            if item.get("webImage"):
                image_url = item["webImage"].get("url")
            
            if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue
            
            # Extract title
            title = item.get("title", "Unknown")
            
            # Extract artist
            artist = item.get("principalOrFirstMaker", "Unknown")
            
            # Extract date
            date = item.get("dating", {}).get("presentingDate", "Unknown")
            
            # Extract origin
            origin = item.get("productionPlaces", [])
            origin = origin[0] if origin else "Unknown"
            
            results.append({
                "title": title,
                "artist": artist,
                "date": date,
                "origin": origin,
                "department": "Rijksmuseum Collection",
                "image_url": image_url,
                "source": "Rijksmuseum"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[rijks] Error: {e}")

    print(f"[rijks] Returning {len(results)} artworks")
    return results