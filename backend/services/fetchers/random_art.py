import random
from backend.registry import SOURCES

def fetch_random_artwork(seen_urls: set[str]):
    all_artworks = []
    for fetcher in SOURCES.values():
        try:
            all_artworks.extend(fetcher())
        except Exception:
            continue
    unseen_artworks = [art for art in all_artworks if art['image_url'] not in seen_urls]
    return random.choice(unseen_artworks) if unseen_artworks else None