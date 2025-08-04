import requests
import random

BASE_URL = "https://api.artic.edu/api/v1"

def get_random_chicago_artwork(seen_urls: set[str]):
    results = []
    try:
        # Try multiple pages to get more diverse artworks
        pages = random.sample(range(1, 200), min(3, 200))
        
        for page in pages:
            response = requests.get(
                f"{BASE_URL}/artworks",
                params={"page": page, "limit": 20, "fields": "id,title,image_id,artist_display,date_display,place_of_origin,department_title"}
            ).json()

            for item in response.get("data", []):
                image_id = item.get("image_id")
                if not image_id:
                    continue
                image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
                if image_url in seen_urls:
                    continue

                results.append({
                    "title": item.get("title"),
                    "artist": item.get("artist_display"),
                    "date": item.get("date_display"),
                    "origin": item.get("place_of_origin"),
                    "department": item.get("department_title"),
                    "image_url": image_url,
                    "source": "chicago"
                })
                
                # Limit results per page
                if len(results) >= 10:
                    break
                    
            # If we have enough results, stop fetching
            if len(results) >= 10:
                break
                
    except Exception as e:
        print(f"[chicago] Error: {e}")
        
    return results

# ✅ Required for the registry to detect and use this fetcher
def fetch_from_chicago(seen_urls: set[str]):
    return get_random_chicago_artwork(seen_urls)