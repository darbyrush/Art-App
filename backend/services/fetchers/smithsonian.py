import requests
from backend.utils import standardize_artwork
import time
import random

API_KEY = "gITD4xyT2v8eBcFSyFaDP3WfbJj9kA52HxUTZsOD"
SEARCH_URL = "https://api.si.edu/openaccess/api/v1.0/search"
DETAIL_URL = "https://api.si.edu/openaccess/api/v1.0/content/"
MAX_RETRIES = 5
RESULTS_PER_PAGE = 10

def fetch_from_smithsonian(seen_urls: set[str] = set()):
    artworks = []
    retry_count = 0
    start_index = random.randint(0, 100)  # start from a random page to reduce repeats

    while retry_count < MAX_RETRIES and len(artworks) == 0:
        params = {
            "api_key": API_KEY,
            "q": "online_media_type:Images",
            "rows": RESULTS_PER_PAGE,
            "start": start_index
        }

        response = requests.get(SEARCH_URL, params=params)
        if not response.ok:
            print(f"[smithsonian] Search failed with status {response.status_code}")
            return artworks

        data = response.json()
        rows = data.get("response", {}).get("rows", [])

        print(f"[smithsonian] Search returned {len(rows)} results at start={start_index}")

        for item in rows:
            obj_id = item.get("id")
            if not obj_id:
                continue

            print(f"[smithsonian] Processing id: {obj_id}")
            detail_res = requests.get(f"{DETAIL_URL}{obj_id}", params={"api_key": API_KEY})
            if not detail_res.ok:
                continue

            try:
                detail = detail_res.json()
                content = detail["content"]["descriptiveNonRepeating"]
                media_list = content.get("online_media", {}).get("media", [])

                if not media_list:
                    print(f"[smithsonian] No media for id {obj_id}")
                    continue

                image_url = media_list[0].get("content")
                if not image_url or image_url.lower().endswith(".gif") or image_url in seen_urls:
                    print(f"[smithsonian] Skipped image {image_url}")
                    continue

                title = content.get("title", "Untitled")
                artist = content.get("record_link", "").split("/")[-1] or "Unknown"

                artworks.append(standardize_artwork({
                    "title": title,
                    "artist": artist,
                    "image_url": image_url,
                    "source": "Smithsonian"
                }))
            except Exception as e:
                print(f"[smithsonian] Error processing {obj_id}: {e}")
                continue

        retry_count += 1
        start_index += RESULTS_PER_PAGE  # go to next batch if needed
        time.sleep(0.3)  # be kind to the API

    print(f"[smithsonian] Returning {len(artworks)} artworks")
    return artworks