import requests
from backend.utils import standardize_artwork, fetch_with_retry, get_cached_data, set_cached_data
from backend.config import config
import time
import random

SEARCH_URL = "https://api.si.edu/openaccess/api/v1.0/search"
MAX_RETRIES = 3
RESULTS_PER_PAGE = 10

def fetch_from_smithsonian(seen_urls: set[str] = set()):
    # Get API key from configuration
    api_key = config.smithsonian_api_key
    if not api_key:
        print("[smithsonian] Warning: No API key found. Set SMITHSONIAN_API_KEY environment variable.")
        return []
    
    artworks = []
    retry_count = 0
    # Try multiple start indices to get more diverse artworks
    start_indices = random.sample(range(0, 200), min(3, 200))

    for start_index in start_indices:
        if len(artworks) >= 10:  # Stop if we have enough
            break
        params = {
            "api_key": api_key,
            "q": "online_media_type:Images",
            "rows": RESULTS_PER_PAGE,
            "start": start_index
        }

        # Check cache first
        cache_key = f"smithsonian_start_{start_index}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print(f"[smithsonian] Using cached data for start={start_index}")
            data = cached_data
        else:
            # Fetch fresh data
            response = fetch_with_retry(SEARCH_URL, params=params)
            if not response or not response.ok:
                print(f"[smithsonian] Search failed with status {response.status_code if response else 'No response'}")
                continue

            data = response.json()
            set_cached_data(cache_key, data)

        rows = data.get("response", {}).get("rows", [])
        print(f"[smithsonian] Search returned {len(rows)} results at start={start_index}")

        for item in rows:
            # The search results already contain the content we need
            content = item.get("content", {})
            if not content:
                continue

            # Extract descriptive information
            descriptive = content.get("descriptiveNonRepeating", {})
            if not descriptive:
                continue

            # Get media information
            online_media = descriptive.get("online_media", {})
            media_list = online_media.get("media", [])
            
            if not media_list:
                continue

            # Get the first media item
            media = media_list[0]
            image_url = media.get("content")
            
            if not image_url or image_url.lower().endswith(".gif") or image_url in seen_urls:
                continue

            # Extract title and artist
            title = descriptive.get("title", {}).get("content", "Untitled")
            if not title or title == "Untitled":
                # Try to get title from freetext
                freetext = content.get("freetext", {})
                publisher = freetext.get("publisher", [])
                if publisher:
                    title = publisher[0].get("content", "Untitled")

            # Extract artist from various possible locations
            artist = "Unknown"
            freetext = content.get("freetext", {})
            name_list = freetext.get("name", [])
            for name_item in name_list:
                if name_item.get("label") in ["Artist", "Creator", "Maker"]:
                    artist = name_item.get("content", "Unknown")
                    break

            # If no artist found, try to extract from record_link
            if artist == "Unknown":
                record_link = descriptive.get("record_link", "")
                if record_link:
                    # Try to extract artist from the URL path
                    parts = record_link.split("/")
                    if len(parts) > 1:
                        artist = parts[-1].replace("_", " ").title()

            artworks.append(standardize_artwork(
                title=title,
                artist=artist,
                image_url=image_url,
                source="Smithsonian"
            ))

        time.sleep(0.1)  # Small delay between requests

    print(f"[smithsonian] Returning {len(artworks)} artworks")
    return artworks