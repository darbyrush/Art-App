import requests

def fetch_from_cleveland():
    response = requests.get(
        "https://openaccess-api.clevelandart.org/api/artworks/",
        params={"has_image": 1, "limit": 100}
    )
    data = response.json()
    artworks = []
    for obj in data.get("data", []):
        if obj.get("images", {}).get("web", {}).get("url"):
            artworks.append({
                "title": obj.get("title"),
                "artist": obj.get("creators", [{}])[0].get("description", "Unknown"),
                "date": obj.get("creation_date", "Unknown"),
                "origin": obj.get("culture", "Unknown"),
                "department": obj.get("department", "Unknown"),
                "source": "Cleveland Museum of Art",
                "image_url": obj["images"]["web"]["url"]
            })
    return artworks