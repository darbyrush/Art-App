import requests
import random

BASE_URL = "https://api.artic.edu/api/v1"

def get_random_chicago_artwork(seen_urls: set[str]):
    try:
        page = random.randint(1, 100)
        response = requests.get(
            f"{BASE_URL}/artworks",
            params={"page": page, "limit": 10, "fields": "id,title,image_id,artist_display,date_display,place_of_origin,department_title"}
        ).json()

        for item in response.get("data", []):
            image_id = item.get("image_id")
            if not image_id:
                continue
            image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            if image_url in seen_urls:
                continue

            return {
                "title": item.get("title"),
                "artist": item.get("artist_display"),
                "date": item.get("date_display"),
                "origin": item.get("place_of_origin"),
                "department": item.get("department_title"),
                "image_url": image_url,
                "source": "Art Institute of Chicago"
            }
    except:
        return None
    return None

# ✅ Required for the registry to detect and use this fetcher
def fetch_from_chicago(seen_urls: set[str]):
    return get_random_chicago_artwork(seen_urls)