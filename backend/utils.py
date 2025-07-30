import json
import os

SEEN_FILE = "seen_urls.json"

def load_seen_urls() -> set[str]:
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    return set()

def save_feedback(art, liked: bool):
    seen = load_seen_urls()
    seen.add(art["image_url"])
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)