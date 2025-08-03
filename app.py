import sys
import os
import hashlib
import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# Ensure backend modules are available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from backend.services.fetchers.random_art import fetch_random_artwork, fetch_artworks_from_sources
from backend.registry import SOURCES  # ✅ Corrected import
from backend.utils import load_seen_urls, save_feedback, clear_cache, get_performance_stats, reset_performance_stats
from backend.config import config

# ------------------- Streamlit Setup -------------------
st.set_page_config(page_title="Gallery", layout="centered")
st.title("Gallery")

# ------------------- State Initialization -------------------
if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = load_seen_urls()

if "selected_sources" not in st.session_state:
    st.session_state.selected_sources = ["all"]

if "art" not in st.session_state:
    st.session_state.art = None

def fetch_filtered_artwork(seen_urls, selected_sources):
    if "all" in selected_sources:
        return fetch_random_artwork(seen_urls)
    
    # Fetch from multiple selected sources
    artworks = fetch_artworks_from_sources(seen_urls, selected_sources)
    if artworks:
        import random
        return random.choice(artworks)
    return None

def test_single_source(source_name):
    """Test a single source and return results"""
    if source_name not in SOURCES:
        return None
    
    try:
        fetcher = SOURCES[source_name]
        result = fetcher(set())
        return result
    except Exception as e:
        st.error(f"Error testing {source_name}: {e}")
        return None

# ------------------- UI Helpers -------------------
def show_artwork(art):
    image_url = art.get('image_url')
    if not image_url:
        st.warning("No image to display.")
        return

    try:
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        if img.format == "GIF":
            st.warning("Skipping GIF image.")
            return
        st.image(image_url, caption=art.get('title', 'Unknown'), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        return

    # Display basic information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Artist:** {art.get('artist', 'Unknown')}")
        st.markdown(f"**Date:** {art.get('date', 'Unknown')}")
        st.markdown(f"**Period:** {art.get('period', 'Unknown')}")
    with col2:
        st.markdown(f"**Origin:** {art.get('origin', 'Unknown')}")
        st.markdown(f"**Medium:** {art.get('medium', 'Unknown')}")
        st.markdown(f"**Gallery:** {art.get('source', 'Unknown')}")
    
    # Display search tags
    if art.get('search_tags'):
        st.markdown("**Tags:** " + ", ".join(art['search_tags']))
    
    # Display additional metadata if available
    if art.get('year'):
        st.markdown(f"**Year:** {art['year']}")
    if art.get('source_category'):
        st.markdown(f"**Museum Type:** {art['source_category']}")

def handle_feedback(liked: bool):
    save_feedback(st.session_state.art, liked=liked)
    st.session_state.seen_urls = load_seen_urls()
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, st.session_state.selected_sources)
    st.rerun()

# ------------------- Main UI -------------------

# Source selection
st.sidebar.header("Gallery Sources")
st.sidebar.markdown("Select which art sources to browse:")

# Available sources
available_sources = ["all"] + list(SOURCES.keys())

# Multi-select for sources
selected_sources = st.sidebar.multiselect(
    "Choose art sources:",
    options=available_sources,
    default=st.session_state.selected_sources,
    help="Select multiple sources to browse from. Choose 'all' to use all sources."
)

# Handle source selection changes
if selected_sources != st.session_state.selected_sources:
    st.session_state.selected_sources = selected_sources
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, selected_sources)
    st.rerun()

# Test Sources Section
st.sidebar.markdown("---")
st.sidebar.markdown("**🧪 Test Sources**")
st.sidebar.markdown("Test individual sources:")

# Test individual sources
for source_name in SOURCES.keys():
    if st.sidebar.button(f"Test {source_name.title()}", key=f"test_{source_name}"):
        with st.spinner(f"Testing {source_name}..."):
            result = test_single_source(source_name)
            if result:
                if isinstance(result, list):
                    st.success(f"{source_name.title()}: Found {len(result)} artworks")
                    if result:
                        st.json(result[0])  # Show first artwork as example
                else:
                    st.success(f"{source_name.title()}: Found 1 artwork")
                    st.json(result)
            else:
                st.error(f"{source_name.title()}: No artworks found")

# API Key Status
st.sidebar.markdown("---")
st.sidebar.markdown("**🔑 API Key Status**")
validation = config.validate_api_keys()
for source, available in validation["available_keys"].items():
    status = "✅" if available else "❌"
    st.sidebar.markdown(f"{status} {source.title()}")

if validation["missing_keys"]:
    st.sidebar.markdown("**Missing API Keys:**")
    for key in validation["missing_keys"]:
        st.sidebar.markdown(f"• {key}")

# Cache management
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑️ Clear Cache"):
        clear_cache()
        st.sidebar.success("Cache cleared!")
with col2:
    if st.button("📊 Reset Stats"):
        reset_performance_stats()
        st.sidebar.success("Stats reset!")

# Performance info
st.sidebar.markdown("---")
st.sidebar.markdown("**📈 Performance Stats**")
stats = get_performance_stats()
st.sidebar.markdown(f"Cache hit rate: {stats['cache_hit_rate']}")
st.sidebar.markdown(f"Avg fetch time: {stats['avg_fetch_time']}")
st.sidebar.markdown(f"Total requests: {stats['total_requests']}")
st.sidebar.markdown(f"Cache size: {stats['cache_size']}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Seen artworks:** {len(st.session_state.seen_urls)}")
st.sidebar.markdown(f"**Selected sources:** {len(selected_sources)}")

# Load initial art if none
if st.session_state.art is None:
    st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, st.session_state.selected_sources)

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
    if st.button("🔄 Refresh Sources"):
        st.session_state.art = fetch_filtered_artwork(st.session_state.seen_urls, st.session_state.selected_sources)
        st.rerun()