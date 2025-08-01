# import requests
# from backend.utils import standardize_artwork

# API_KEY = "your-rijksmuseum-api-key"
# BASE_URL = "https://www.rijksmuseum.nl/api/en/collection"

# def fetch_from_rijks():
#     params = {
#         "key": API_KEY,
#         "format": "json",
#         "imgonly": True,
#         "ps": 50  # page size
#     }
#     response = requests.get(BASE_URL, params=params)
#     data = response.json()

#     artworks = []
#     for item in data.get("artObjects", []):
#         artworks.append(standardize_artwork({
#             "title": item.get("title"),
#             "artist": item.get("principalOrFirstMaker"),
#             "image_url": item.get("webImage", {}).get("url"),
#             "source": "rijks"
#         }))
#     return artworks