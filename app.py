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
from frontend.utils import load_feedback_df, save_feedback, clear_feedback_csv, get_user_liked_artworks, get_user_stats
from frontend.auth import is_logged_in, get_current_user, logout_user, render_login_page

# Page configuration
st.set_page_config(
    page_title="Art Explorer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with focus on images
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
    
    .artwork-showcase {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
    }
    
    .artwork-image-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 400px;
    }
    
    .artwork-image {
        max-width: 100%;
        max-height: 500px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .artwork-image:hover {
        transform: scale(1.02);
    }
    
    .artwork-info {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .artwork-title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .artwork-artist {
        font-size: 1.3rem;
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .artwork-details {
        background: rgba(255,255,255,0.8);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .feedback-buttons {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .like-button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        cursor: pointer;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
    }
    
    .like-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
    }
    
    .dislike-button {
        background: linear-gradient(45deg, #f44336, #da190b);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        cursor: pointer;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(244, 67, 54, 0.3);
        transition: all 0.3s ease;
    }
    
    .dislike-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(244, 67, 54, 0.4);
    }
    
    .new-artwork-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 1.5rem 3rem;
        border-radius: 50px;
        cursor: pointer;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .new-artwork-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
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
    
    .user-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        margin: 2rem 0;
    }
    
    .empty-state h2 {
        color: #667eea;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .empty-state p {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_artwork' not in st.session_state:
    st.session_state.current_artwork = None
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = ['all']

# Check if user is logged in
if not is_logged_in():
    render_login_page()
    st.stop()

# User is logged in - show main app
current_user = get_current_user()
username = st.session_state.get('username', 'User')

# Main header with user info
st.markdown(f'<h1 class="main-header">🎨 Art Explorer</h1>', unsafe_allow_html=True)

# User info section
st.markdown(f"""
<div class="user-info">
    <h3>Welcome, {username}! 👋</h3>
    <p>Discover and collect art from world-class museums.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # User section
    st.markdown("---")
    st.subheader(f"👤 {username}")
    
    if st.button("🚪 Logout", help="Logout from your account"):
        logout_user()
        st.success("Logged out successfully!")
        st.rerun()
    
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

# Main content area - Focus on the artwork image
st.markdown('<div class="artwork-showcase">', unsafe_allow_html=True)

# Get New Artwork Button - Prominent placement
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎲 Get New Artwork", key="new_artwork_btn", help="Fetch a new random artwork"):
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

# Display current artwork with focus on the image
if st.session_state.current_artwork:
    artwork = st.session_state.current_artwork
    
    # Artwork title and artist
    st.markdown(f"""
    <div class="artwork-info">
        <div class="artwork-title">{artwork.get('title', 'Untitled')}</div>
        <div class="artwork-artist">by {artwork.get('artist', 'Unknown Artist')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Large, prominent image display
    if artwork.get('image_url'):
        st.markdown('<div class="artwork-image-container">', unsafe_allow_html=True)
        st.image(
            artwork['image_url'], 
            use_container_width=True, 
            caption="",
            output_format="PNG"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Artwork details in an expandable section
    with st.expander("📋 Artwork Details", expanded=False):
        st.markdown(f"""
        <div class="artwork-details">
            <strong>Date:</strong> {artwork.get('date', 'Unknown')}<br>
            <strong>Origin:</strong> {artwork.get('origin', 'Unknown')}<br>
            <strong>Department:</strong> {artwork.get('department', 'Unknown')}<br>
            <strong>Source:</strong> {artwork.get('source', 'Unknown')}
        </div>
        """, unsafe_allow_html=True)
    
    # Feedback buttons - Prominent and centered
    st.markdown('<div class="feedback-buttons">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("👍 Like", key="like_btn", help="Save this artwork to your gallery"):
            if st.session_state.current_artwork:
                save_feedback(st.session_state.current_artwork, "like", user_id=current_user)
                st.success("Artwork saved to your gallery!")
    
    with col2:
        if st.button("👎 Dislike", key="dislike_btn", help="Mark this artwork as disliked"):
            if st.session_state.current_artwork:
                save_feedback(st.session_state.current_artwork, "dislike", user_id=current_user)
                st.success("Feedback recorded!")
    
    with col3:
        if st.button("🎲 Next Artwork", key="next_artwork_btn", help="Get another random artwork"):
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
                    st.rerun()
                else:
                    st.error("No artwork found. Try different sources or check your internet connection.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # Empty state with prominent call-to-action
    st.markdown("""
    <div class="empty-state">
        <h2>🎨 Ready to Discover Art?</h2>
        <p>Click the button above to start exploring beautiful artworks from world-class museums.</p>
        <p>Choose your favorite sources in the sidebar to customize your experience.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User's gallery stats in a smaller section below
st.markdown("---")
st.subheader("📈 Your Gallery Stats")

# Get user-specific stats
user_stats = get_user_stats(current_user)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Liked Artworks", user_stats['liked_artworks'])
with col2:
    st.metric("Museums", user_stats['unique_museums'])
with col3:
    st.metric("Total Interactions", user_stats['total_artworks'])
with col4:
    if user_stats['liked_artworks'] > 0:
        avg_rating = user_stats['avg_rating']
        st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
    else:
        st.metric("Avg Rating", "0⭐")

# Show recent likes
liked_df = get_user_liked_artworks(current_user)
if not liked_df.empty:
    st.write("**Recent additions to your gallery:**")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(liked_df.tail(3).iterrows()):
        with cols[idx]:
            title = row.get('title', 'Untitled')
            if len(title) > 25:
                title = title[:25] + "..."
            st.write(f"• {title}")
            st.write(f"  by {row.get('artist', 'Unknown')[:20]}...")
else:
    st.write("No liked artworks yet. Start exploring!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    🎨 Art Explorer | Discover, Filter, and Collect Art from World-Class Museums
</div>
""", unsafe_allow_html=True)