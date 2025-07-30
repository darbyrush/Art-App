import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests_cache

# --------------------------
# Thread-safe caching setup
# --------------------------
_thread_local = threading.local()

def get_session():
    if not hasattr(_thread_local, "session"):
        _thread_local.session = requests_cache.CachedSession(
            "art_api_cache", expire_after=3600  # 1 hour cache
        )
    return _thread_local.session

def is_valid_url(url):
    return isinstance(url, str) and url.startswith("http")

# --------------------------
# Fetchers by Museum Source
# --------------------------

def fetch_from_chicago(seen_urls):
    session = get_session()
    base_url = "https://api.artic.edu/api/v1/artworks"
    fields = "id,title,image_id,artist_display,date_display,place_of_origin,department_display"

    for _ in range(10):
        page = random.randint(1, 1000)
        res = session.get(f"{base_url}?fields={fields}&limit=1&page={page}")
        if not res.ok:
            continue

        data = res.json().get("data", [])
        if not data:
            continue

        art = data[0]
        image_id = art.get("image_id")
        if not image_id:
            continue

        image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
        if not is_valid_url(image_url) or image_url in seen_urls:
            continue

        return {
            "title": art.get("title", "Untitled"),
            "image_url": image_url,
            "artist": art.get("artist_display", "Unknown"),
            "date": art.get("date_display", "Unknown"),
            "origin": art.get("place_of_origin", "Unknown"),
            "department": art.get("department_display", "Unknown"),
            "source": "Art Institute of Chicago",
        }
    return None

def fetch_from_met(seen_urls):
    session = get_session()
    ids_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    res = session.get(ids_url)
    if not res.ok:
        return None

    all_ids = res.json().get("objectIDs", [])
    if not all_ids:
        return None

    for _ in range(10):
        obj_id = random.choice(all_ids)
        obj_res = session.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}")
        if not obj_res.ok:
            continue

        obj = obj_res.json()
        image_url = obj.get("primaryImageSmall")
        if not is_valid_url(image_url) or image_url in seen_urls:
            continue

        return {
            "title": obj.get("title", "Untitled"),
            "image_url": image_url,
            "artist": obj.get("artistDisplayName", "Unknown"),
            "date": obj.get("objectDate", "Unknown"),
            "origin": obj.get("country", "Unknown"),
            "department": obj.get("department", "Unknown"),
            "source": "The Met",
        }
    return None

def fetch_from_cleveland(seen_urls):
    session = get_session()
    base_url = "https://openaccess-api.clevelandart.org/api/artworks"

    for _ in range(10):
        page = random.randint(1, 1000)
        res = session.get(f"{base_url}?has_image=1&limit=20&page={page}")
        if not res.ok:
            continue

        artworks = res.json().get("data", [])
        if not artworks:
            continue

        for art in artworks:
            image_info = art.get("images", {}).get("web", {})
            image_url = image_info.get("url", "")
            if not is_valid_url(image_url) or image_url in seen_urls:
                continue

            return {
                "title": art.get("title", "Untitled"),
                "image_url": image_url,
                "artist": art.get("creators", [{}])[0].get("description", "Unknown"),
                "date": art.get("creation_date", "Unknown"),
                "origin": art.get("creation_place", "Unknown"),
                "department": art.get("department", "Unknown"),
                "source": "Cleveland Museum of Art",
            }
    return None

# --------------------------
# Dispatcher
# --------------------------

ART_SOURCES = {
    "chicago": fetch_from_chicago,
    "met": fetch_from_met,
    "cleveland": fetch_from_cleveland,
}

def fetch_random_artwork(seen_urls):
    if not isinstance(seen_urls, set):
        seen_urls = set()
    else:
        seen_urls = {url for url in seen_urls if is_valid_url(url)}

    with ThreadPoolExecutor(max_workers=len(ART_SOURCES)) as executor:
        futures = {
            executor.submit(fetcher, seen_urls): name
            for name, fetcher in ART_SOURCES.items()
        }

        for future in as_completed(futures):
            try:
                art = future.result()
                if art:
                    return art
            except Exception as e:
                print(f"⚠️ Error fetching from {futures[future]}: {e}")
    return None