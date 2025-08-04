import streamlit as st
import pandas as pd
import json
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image
import hashlib
import os

# Ensure backend modules are available
import sys
sys.path.append('.')

from backend.services.fetchers.random_art import fetch_random_artwork, fetch_artworks_from_sources
from backend.utils import get_performance_stats, reset_performance_stats, clear_cache
from frontend.utils import load_feedback_df, save_feedback, clear_feedback_csv

# Page configuration
st.set_page_config(
    page_title="Art Explorer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .artwork-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .artwork-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .artwork-artist {
        font-size: 1.1rem;
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    
    .artwork-details {
        background: rgba(255,255,255,0.7);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .button-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .like-button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .dislike-button {
        background: linear-gradient(45deg, #f44336, #da190b);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .source-option {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_artwork' not in st.session_state:
    st.session_state.current_artwork = None
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = ['all']

# Main header
st.markdown('<h1 class="main-header">🎨 Art Explorer</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # Filter section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("🔍 Filter Art Sources")
    
    # Source selection
    available_sources = ['all', 'cleveland', 'met', 'chicago', 'walters', 'national_gallery', 'smithsonian', 'harvard']
    selected_sources = st.multiselect(
        "Select art sources:",
        available_sources,
        default=st.session_state.selected_sources,
        help="Choose which museums to fetch art from"
    )
    
    if selected_sources != st.session_state.selected_sources:
        st.session_state.selected_sources = selected_sources
        st.session_state.current_artwork = None  # Reset current artwork when sources change
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance stats
    st.markdown("---")
    st.subheader("📊 Performance Stats")
    stats = get_performance_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        # Handle cache_hit_rate which might be a string
        cache_hit_rate = stats['cache_hit_rate']
        if isinstance(cache_hit_rate, str):
            cache_hit_rate = cache_hit_rate.replace('%', '')
        try:
            cache_hit_rate_float = float(cache_hit_rate)
            st.metric("Cache Hit Rate", f"{cache_hit_rate_float:.1f}%")
        except (ValueError, TypeError):
            st.metric("Cache Hit Rate", f"{cache_hit_rate}")
        
        st.metric("Total Requests", stats['total_requests'])
    with col2:
        # Handle avg_fetch_time which might be a string
        avg_fetch_time = stats['avg_fetch_time']
        if isinstance(avg_fetch_time, str):
            avg_fetch_time = avg_fetch_time.replace('s', '')
        try:
            avg_fetch_time_float = float(avg_fetch_time)
            st.metric("Avg Fetch Time", f"{avg_fetch_time_float:.2f}s")
        except (ValueError, TypeError):
            st.metric("Avg Fetch Time", f"{avg_fetch_time}")
        
        st.metric("Cache Size", f"{stats['cache_size']} items")
    
    # Control buttons
    st.markdown("---")
    st.subheader("🛠️ Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Cache", help="Clear all cached data"):
            clear_cache()
            st.success("Cache cleared!")
    
    with col2:
        if st.button("🔄 Reset Stats", help="Reset performance statistics"):
            reset_performance_stats()
            st.success("Stats reset!")
    
    # Test Sources Section
    st.markdown("---")
    st.subheader("🧪 Test Sources")
    st.markdown("Test individual sources:")
    
    # Test individual sources
    for source_name in ['cleveland', 'met', 'chicago', 'walters', 'national_gallery', 'smithsonian', 'harvard']:
        if st.button(f"Test {source_name.title()}", key=f"test_{source_name}"):
            with st.spinner(f"Testing {source_name}..."):
                try:
                    from backend.registry import SOURCES
                    if source_name in SOURCES:
                        result = SOURCES[source_name](set())
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
                    else:
                        st.error(f"{source_name.title()}: Source not available")
                except Exception as e:
                    st.error(f"Error testing {source_name}: {e}")
    
    # Gallery link
    st.markdown("---")
    st.subheader("🖼️ Your Gallery")
    st.write("**View your saved artworks with filtering and analytics!**")
    
    if st.button("🎨 Open Gallery", help="Go to your dedicated gallery page"):
        st.switch_page("pages/1_gallery.py")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Artwork display area
    st.subheader("🖼️ Discover Art")
    
    if st.button("🎲 Get New Artwork", help="Fetch a new random artwork"):
        with st.spinner("Fetching new artwork..."):
            if 'all' in st.session_state.selected_sources:
                artwork = fetch_random_artwork(set())
            else:
                artwork = fetch_artworks_from_sources(st.session_state.selected_sources, set())
                if artwork and isinstance(artwork, list):
                    artwork = artwork[0] if artwork else None
            
            if artwork:
                st.session_state.current_artwork = artwork
                st.success("New artwork loaded!")
            else:
                st.error("No artwork found. Try different sources or check your internet connection.")
    
    # Display current artwork
    if st.session_state.current_artwork:
        artwork = st.session_state.current_artwork
        
        # Artwork card
        st.markdown(f"""
        <div class="artwork-card">
            <div class="artwork-title">{artwork.get('title', 'Untitled')}</div>
            <div class="artwork-artist">by {artwork.get('artist', 'Unknown Artist')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Image
        if artwork.get('image_url'):
            st.image(artwork['image_url'], use_container_width=True, caption="Artwork Image")
        
        # Details
        with st.expander("📋 Artwork Details", expanded=True):
            st.markdown(f"""
            <div class="artwork-details">
                <strong>Date:</strong> {artwork.get('date', 'Unknown')}<br>
                <strong>Origin:</strong> {artwork.get('origin', 'Unknown')}<br>
                <strong>Department:</strong> {artwork.get('department', 'Unknown')}<br>
                <strong>Source:</strong> {artwork.get('source', 'Unknown')}
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback buttons
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("👍 Like", key="like_btn", help="Save this artwork to your gallery"):
                if st.session_state.current_artwork:
                    save_feedback(st.session_state.current_artwork, "like")
                    st.success("Artwork saved to gallery!")
        
        with col2:
            if st.button("👎 Dislike", key="dislike_btn", help="Mark this artwork as disliked"):
                if st.session_state.current_artwork:
                    save_feedback(st.session_state.current_artwork, "dislike")
                    st.success("Feedback recorded!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.info("Click 'Get New Artwork' to start exploring!")

with col2:
    # Quick gallery stats
    st.subheader("📈 Gallery Stats")
    
    # Load gallery data
    df = load_feedback_df()
    if not df.empty and "liked" in df.columns:
        df["liked"] = df["liked"].astype(str).str.lower().map({
            "true": True, "false": False, "like": True, "dislike": False
        }).fillna(False)
        
        liked_count = len(df[df["liked"]])
        if liked_count > 0:
            st.metric("Liked Artworks", liked_count)
            st.metric("Museums", df[df['liked']]['source'].nunique())
            
            # Show recent likes
            recent_likes = df[df["liked"]].tail(3)
            if not recent_likes.empty:
                st.write("**Recent additions:**")
                for _, row in recent_likes.iterrows():
                    st.write(f"• {row.get('title', 'Untitled')[:30]}...")
        else:
            st.write("No liked artworks yet. Start exploring!")
    else:
        st.write("No gallery yet. Start exploring!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    🎨 Art Explorer | Discover, Filter, and Collect Art from World-Class Museums
</div>
""", unsafe_allow_html=True)