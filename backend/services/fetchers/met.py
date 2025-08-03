import requests
import random
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def fetch_from_met(seen_urls: set[str] = set()):
    results = []
    try:
        # Get a list of object IDs first
        search_resp = fetch_with_retry(f"{BASE_URL}/search", params={"hasImages": True, "q": "*"})
        if not search_resp or not search_resp.ok:
            return results
            
        search_data = search_resp.json()
        object_ids = search_data.get("objectIDs", [])
        
        if not object_ids:
            return results
            
        # Sample random object IDs
        sample_size = min(10, len(object_ids))
        sampled_ids = random.sample(object_ids, sample_size)
        
        for object_id in sampled_ids:
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

            results.append({
                "title": data.get("title", "Unknown"),
                "artist": data.get("artistDisplayName", "Unknown"),
                "date": data.get("objectDate", "Unknown"),
                "origin": data.get("culture") or data.get("country", "Unknown"),
                "department": data.get("department", "Unknown"),
                "image_url": image_url,
                "source": "Metropolitan Museum of Art"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[met] Error: {e}")

    return results