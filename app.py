import sys
import os
import hashlib
import streamlit as st

# Add backend/frontend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.art_sources import fetch_random_artwork
from frontend.utils import load_seen_urls, save_feedback

st.set_page_config(page_title="Art Explorer", layout="centered")
st.title("🎨 Do You Like This Painting?")

# ------------------- Initial State Setup -------------------
if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = load_seen_urls()

if "art" not in st.session_state:
    st.session_state.art = fetch_random_artwork(st.session_state.seen_urls)
    st.session_state._just_loaded = True
    st.rerun()

# Avoid double-render on first load
if st.session_state.get("_just_loaded", False):
    st.session_state._just_loaded = False

# ------------------- UI Logic -------------------
def show_artwork(art):
    st.image(art['image_url'], caption=art['title'], use_container_width=True)
    st.markdown(f"**Artist:** {art['artist']}")
    st.markdown(f"**Date:** {art['date']}")
    st.markdown(f"**Place of Origin:** {art['origin']}")
    st.markdown(f"**Department:** {art['department']}")
    st.markdown(f"**Gallery:** {art['source']}")

def handle_feedback(liked: bool):
    save_feedback(st.session_state.art, liked=liked)
    st.session_state.seen_urls = load_seen_urls()
    st.session_state.art = fetch_random_artwork(st.session_state.seen_urls)
    st.rerun()

# ------------------- Main Render -------------------
art = st.session_state.art

if art:
    show_artwork(art)

    # Use hash of URL for button keys
    image_key = hashlib.md5(art['image_url'].encode()).hexdigest()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Like", key=f"like_{image_key}"):
            handle_feedback(True)
    with col2:
        if st.button("👎 Dislike", key=f"dislike_{image_key}"):
            handle_feedback(False)
else:
    st.warning("🎉 You've viewed all available artworks for now!")