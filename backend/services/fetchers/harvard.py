import requests
from backend.utils import standardize_artwork

API_KEY = "793df6db-fd3c-4a46-bb9d-dbf69820f910"
BASE_URL = "https://api.harvardartmuseums.org/object"

def fetch_from_harvard():
    params = {
        "apikey": API_KEY,
        "hasimage": 1,
        "size": 50
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    artworks = []
    for item in data.get("records", []):
        artworks.append(standardize_artwork(
            title=item.get("title"),
            artist=item.get("people", [{}])[0].get("name") if item.get("people") else "Unknown",
            image_url=item.get("primaryimageurl"),
            source="harvard"
        ))
    return artworks