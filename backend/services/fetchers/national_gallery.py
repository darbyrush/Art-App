import requests
import random
import csv
from io import StringIO
from backend.utils import fetch_with_retry, get_cached_data, set_cached_data

# National Gallery of Art open data files
OBJECTS_URL = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/objects.csv"
IMAGES_URL = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/published_images.csv"
CONSTITUENTS_URL = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/constituents.csv"

def convert_iiif_to_image_url(iiif_url):
    """Convert IIIF URL to a displayable image URL"""
    if not iiif_url:
        return None
    
    # Convert IIIF URL to a proper image URL
    # Format: https://api.nga.gov/iiif/{uuid}/full/800,/0/default.jpg
    if iiif_url.startswith("https://api.nga.gov/iiif/"):
        # Extract the UUID from the IIIF URL
        uuid = iiif_url.split("/")[-1]
        # Create a proper image URL with reasonable dimensions
        return f"https://api.nga.gov/iiif/{uuid}/full/800,/0/default.jpg"
    
    return iiif_url

def fetch_from_national_gallery(seen_urls: set[str] = set()):
    results = []
    try:
        # Check cache first
        cache_key = "national_gallery_data"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            print("[national_gallery] Using cached data")
            objects_data, images_data, constituents_data = cached_data
        else:
            # Fetch objects data
            objects_response = fetch_with_retry(OBJECTS_URL)
            if not objects_response or not objects_response.ok:
                print(f"[national_gallery] Objects data request failed with status {objects_response.status_code if objects_response else 'No response'}")
                return results
            
            # Fetch images data
            images_response = fetch_with_retry(IMAGES_URL)
            if not images_response or not images_response.ok:
                print(f"[national_gallery] Images data request failed with status {images_response.status_code if images_response else 'No response'}")
                return results
            
            # Fetch constituents data
            constituents_response = fetch_with_retry(CONSTITUENTS_URL)
            if not constituents_response or not constituents_response.ok:
                print(f"[national_gallery] Constituents data request failed with status {constituents_response.status_code if constituents_response else 'No response'}")
                return results
            
            # Parse CSV data
            objects_data = list(csv.DictReader(StringIO(objects_response.text)))
            images_data = list(csv.DictReader(StringIO(images_response.text)))
            constituents_data = list(csv.DictReader(StringIO(constituents_response.text)))
            
            # Cache the data
            set_cached_data(cache_key, (objects_data, images_data, constituents_data))
        
        # Create a mapping of object IDs to image URLs
        images_map = {}
        for image_item in images_data:
            object_id = image_item.get('depictstmsobjectid')
            if object_id and image_item.get('viewtype') == 'primary':
                # Use the base IIIF URL and convert it to a proper image URL
                iiif_url = image_item.get('iiifurl')
                if iiif_url:
                    image_url = convert_iiif_to_image_url(iiif_url)
                    if image_url:
                        images_map[object_id] = image_url
        
        # Create a mapping of constituent IDs to names
        constituents_map = {}
        for constituent_item in constituents_data:
            constituent_id = constituent_item.get('constituentid')
            if constituent_id:
                name = constituent_item.get('displayname', 'Unknown')
                constituents_map[constituent_id] = name
        
        # Process art objects
        for object_item in objects_data:
            object_id = object_item.get('objectid')
            if not object_id:
                continue
            
            # Get image URL
            image_url = images_map.get(object_id)
            if not image_url or image_url in seen_urls:
                continue
            
            # Extract title
            title = object_item.get('title', 'Unknown')
            
            # Extract artist/creator (we'll need to look up constituent info)
            attribution = object_item.get('attribution', 'Unknown')
            
            # Extract date
            display_date = object_item.get('displaydate', 'Unknown')
            
            # Extract medium
            medium = object_item.get('medium', 'Unknown')
            
            # Extract classification
            classification = object_item.get('classification', 'Unknown')
            
            results.append({
                "title": title,
                "artist": attribution,
                "date": display_date,
                "origin": "National Gallery of Art Collection",
                "department": classification,
                "image_url": image_url,
                "source": "National Gallery of Art"
            })
            
            # Limit results
            if len(results) >= 5:
                break
                
    except Exception as e:
        print(f"[national_gallery] Error: {e}")

    print(f"[national_gallery] Returning {len(results)} artworks")
    return results 