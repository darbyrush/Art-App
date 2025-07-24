import requests

response = requests.get("https://openaccess-api.clevelandart.org/api/artworks?has_image=1&limit=1&page=1")
data = response.json().get("data", [])
if data:
    artwork = data[0]
    image_url = artwork.get("images", {}).get("web", "")
    print("Title:", artwork.get("title"))
    print("Image URL:", image_url)
else:
    print("No artwork found.")