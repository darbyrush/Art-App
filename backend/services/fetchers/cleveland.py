import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://openaccess-api.clevelandart.org/api/artworks"

def fetch_from_cleveland(seen_urls: set[str]):
    results = []
    try:
        page = random.randint(1, 50)
        
        # Check cache first
        cache_key = f"cleveland_page_{page}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print(f"[cleveland] Using cached data for page {page}")
            data = cached_data
        else:
            # Fetch fresh data
            resp = fetch_with_retry(BASE_URL, params={"page": page, "limit": 10, "has_image": True})
            if not resp or not resp.ok:
                return results
            
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
                "source": "Cleveland Museum of Art"
            })
    except Exception as e:
        print(f"[cleveland] Error: {e}")

    return results