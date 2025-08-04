import requests
import random
import csv
from io import StringIO
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

# Walters Art Museum static data files
ART_URL = "https://raw.githubusercontent.com/WaltersArtMuseum/api-thewalters-org/main/art.csv"
MEDIA_URL = "https://raw.githubusercontent.com/WaltersArtMuseum/api-thewalters-org/main/media.csv"

def fetch_from_walters(seen_urls: set[str] = set()):
    results = []
    try:
        # Check cache first
        cache_key = "walters_data"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print("[walters] Using cached data")
            art_data, media_data = cached_data
        else:
            # Fetch art data
            art_response = fetch_with_retry(ART_URL)
            if not art_response or not art_response.ok:
                print(f"[walters] Art data request failed with status {art_response.status_code if art_response else 'No response'}")
                return results
            
            # Fetch media data
            media_response = fetch_with_retry(MEDIA_URL)
            if not media_response or not media_response.ok:
                print(f"[walters] Media data request failed with status {media_response.status_code if media_response else 'No response'}")
                return results
            
            # Parse CSV data
            art_data = list(csv.DictReader(StringIO(art_response.text)))
            media_data = list(csv.DictReader(StringIO(media_response.text)))
            
            # Cache the data
            set_cached_data(cache_key, (art_data, media_data))
        
        # Create a mapping of object IDs to primary image URLs
        media_map = {}
        for media_item in media_data:
            object_id = media_item.get('ObjectID')
            if object_id and media_item.get('MediaType') == 'Image' and media_item.get('IsPrimary') == '1':
                image_url = media_item.get('ImageURL')
                if image_url:
                    media_map[object_id] = image_url
        
        # Process art objects
        for art_item in art_data:
            object_id = art_item.get('ObjectID')
            if not object_id:
                continue
            
            # Get image URL
            image_url = media_map.get(object_id)
            if not image_url or image_url in seen_urls or image_url.lower().endswith(".gif"):
                continue
            
            # Extract title
            title = art_item.get('Title', 'Unknown')
            
            # Extract artist/creator
            artist = art_item.get('Creators', 'Unknown')
            
            # Extract date
            date = art_item.get('DateText', 'Unknown')
            
            # Extract origin/culture
            origin = art_item.get('Culture', 'Unknown')
            
            # Extract medium
            medium = art_item.get('Medium', 'Unknown')
            
            results.append({
                "title": title,
                "artist": artist,
                "date": date,
                "origin": origin,
                "department": "Walters Art Museum Collection",
                "image_url": image_url,
                "source": "walters"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[walters] Error: {e}")

    print(f"[walters] Returning {len(results)} artworks")
    return results 