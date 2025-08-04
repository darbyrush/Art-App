import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://openaccess-api.clevelandart.org/api/artworks"

def fetch_from_cleveland(seen_urls: set[str]):
    results = []
    try:
        # Try multiple pages to get more diverse artworks
        pages = random.sample(range(1, 100), min(3, 100))  # Try 3 random pages
        
        for page in pages:
            # Check cache first
            cache_key = f"cleveland_page_{page}"
            cached_data = get_cached_data(cache_key)
            
            if cached_data:
                print(f"[cleveland] Using cached data for page {page}")
                data = cached_data
            else:
                # Fetch fresh data
                resp = fetch_with_retry(BASE_URL, params={"page": page, "limit": 20, "has_image": True})
                if not resp or not resp.ok:
                    continue
                
                data = resp.json()
                set_cached_data(cache_key, data)

            for item in data.get("data", []):
                # Check if item has images
                images = item.get("images", {})
                if not images:
                    continue
                    
                # Extract image URL - prefer web, then print, then full
                image_url = None
                if isinstance(images, dict):
                    image_url = (
                        images.get("web", {}).get("url")
                        or images.get("print", {}).get("url")
                        or images.get("full", {}).get("url")
                    )

                if not image_url:
                    continue
                if image_url in seen_urls or image_url.lower().endswith(".gif"):
                    continue

                # Extract artist information
                creators = item.get("creators", [])
                artist = "Unknown"
                if creators and isinstance(creators, list) and len(creators) > 0:
                    artist = creators[0].get("description", "Unknown")

                results.append({
                    "title": item.get("title", "Unknown"),
                    "artist": artist,
                    "date": item.get("creation_date", "Unknown"),
                    "origin": item.get("culture", ["Unknown"])[0] if isinstance(item.get("culture"), list) else item.get("culture", "Unknown"),
                    "department": item.get("department", "Unknown"),
                    "image_url": image_url,
                    "source": "cleveland"
                })
                
                # Limit results per page to avoid overwhelming
                if len(results) >= 15:
                    break
                    
            # If we have enough results, stop fetching
            if len(results) >= 15:
                break
                
    except Exception as e:
        print(f"[cleveland] Error: {e}")

    print(f"[cleveland] Returning {len(results)} artworks")
    return results