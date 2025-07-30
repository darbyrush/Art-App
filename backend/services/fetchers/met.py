import requests
import random

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def fetch_from_met():
    results = []
    try:
        for _ in range(5):  # fetch 5 at a time
            object_id = random.randint(1, 900000)
            resp = requests.get(f"{BASE_URL}/objects/{object_id}")
            if not resp.ok:
                continue
            data = resp.json()
            if not data.get("primaryImageSmall"):
                continue

            results.append({
                "title": data.get("title"),
                "artist": data.get("artistDisplayName"),
                "date": data.get("objectDate"),
                "origin": data.get("culture") or data.get("country"),
                "department": data.get("department"),
                "image_url": data.get("primaryImageSmall"),
                "source": "Metropolitan Museum of Art"
            })
    except:
        pass

    return results