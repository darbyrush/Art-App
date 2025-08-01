import sys
import os
import hashlib
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Ensure backend modules are available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.services.fetchers.random_art import fetch_random_artwork
from backend.registry import SOURCES  # ✅ Corrected import
from backend.utils import load_seen_urls, save_feedback

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Art Explorer", layout="centered")
st.title("🎨 Do You Like This Painting?")

# ------------------- State Initialization -------------------
if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = load_seen_urls()

if "selected_source" not in st.session_state:
    st.session_state.selected_source = "all"

if "art" not in st.session_state:
    st.session_state.art = None

def fetch_filtered_artwork(seen_urls, selected_source):
    if selected_source == "all":
        return fetch_random_artwork(seen_urls)

    fetcher = SOURCES.get(selected_source)
    if not fetcher:
        return None

    try:
        result = fetcher(seen_urls)
    except TypeError:
        result = fetcher()

    # If result is a dict, wrap it in a list
    if isinstance(result, dict):
        artworks = [result]
    elif isinstance(result, list):
        artworks = result
    else:
        return None  # Handle string, None, etc.

    for art in artworks:
        if not isinstance(art, dict):
            continue
        if art.get("image_url") and art["image_url"].lower().endswith(".gif"):
            continue
        if art.get("image_url") and art["image_url"] not in seen_urls:
            return art

    return None

# ------------------- UI Helpers -------------------
def show_artwork(art):
    image_url = art.get('image_url')
    if not image_url:
        st.warning("No image to display.")
        return

    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        if img.format == "GIF":
            st.warning("Skipping GIF image.")
            return
        st.image(image_url, caption=art.get('title', 'Unknown'), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        return

    st.markdown(f"**Artist:** {art.get('artist', 'Unknown')}")
    st.markdown(f"**Date:** {art.get('date', 'Unknown')}")
    st.markdown(f"**Place of Origin:** {art.get('origin', 'Unknown')}")
    st.markdown(f"**Department:** {art.get('department', 'Unknown')}")
    st.markdown(f"**Gallery:** {art.get('source', 'Unknown')}")

def handle_feedback(liked: bool):
    save_feedback(st.session_state.art, liked=liked)
    st.session_state.seen_urls = load_seen_urls()
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, st.session_state.selected_source)
    st.rerun()

# ------------------- Main UI -------------------

# Source filter dropdown
sources = ["all"] + list(SOURCES.keys())  # ✅ Uses correct SOURCES reference
selected = st.selectbox("Choose art source:", sources, index=sources.index(st.session_state.selected_source))

if selected != st.session_state.selected_source:
    st.session_state.selected_source = selected
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, selected)
    st.rerun()

# Load initial art if none
if st.session_state.art is None:
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, st.session_state.selected_source)

art = st.session_state.art

if art:
    show_artwork(art)

    image_url = art.get('image_url')
    if image_url:
        image_key = hashlib.md5(image_url.encode()).hexdigest()
    else:
        image_key = "no_image"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Like", key=f"like_{image_key}"):
            handle_feedback(True)
    with col2:
        if st.button("👎 Dislike", key=f"dislike_{image_key}"):
            handle_feedback(False)
else:
    st.warning("🎉 You've viewed all available artworks for now!")