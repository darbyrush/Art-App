import requests
import random

BASE_URL = "https://openaccess-api.clevelandart.org/api/artworks"

def fetch_from_cleveland(seen_urls: set[str]):
    results = []
    try:
        page = random.randint(1, 50)
        resp = requests.get(BASE_URL, params={"page": page, "limit": 10, "has_image": True})
        if not resp.ok:
            return results

        data = resp.json()
        for item in data.get("data", []):
            image_data = item.get("images", {})
            image_url = (
                image_data.get("web")
                or image_data.get("print")
                or image_data.get("full")
                or ""
            )

            if not isinstance(image_url, str) or not image_url:
                continue
            if image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue

            results.append({
                "title": item.get("title", "Unknown"),
                "artist": (item.get("creators") or [{}])[0].get("description", "Unknown"),
                "date": item.get("creation_date", "Unknown"),
                "origin": item.get("culture", "Unknown"),
                "department": item.get("department", "Unknown"),
                "image_url": image_url,
                "source": "Cleveland Museum of Art"
            })
    except Exception as e:
        print(f"[cleveland] Error: {e}")

    return results