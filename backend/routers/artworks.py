# backend/routers/artworks.py
from fastapi import APIRouter, Query
from backend.services.fetchers.random_art import fetch_random_artwork

router = APIRouter()

@router.get("/artworks/random")
def get_random_art(seen_urls: list[str] = Query(default=[])):
    seen_set = set(seen_urls)
    art = fetch_random_artwork(seen_set)
    return art or {"message": "No new artworks available."}