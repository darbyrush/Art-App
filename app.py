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
from frontend.utils import save_feedback, get_user_stats
from frontend.auth import is_logged_in, get_current_user, logout_user, render_login_page

# Page configuration
st.set_page_config(
    page_title="Art Explorer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Instagram-style design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .instagram-container {
        max-width: 600px;
        margin: 0 auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        overflow: hidden;
        position: relative;
    }
    
    .artwork-header {
        padding: 1rem;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .artwork-source {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.1rem;
    }
    
    .artwork-image-container {
        position: relative;
        width: 100%;
        height: 600px;
        overflow: hidden;
        cursor: pointer;
    }
    
    .artwork-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    
    .artwork-image:hover {
        transform: scale(1.02);
    }
    
    .double-tap-overlay {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 4rem;
        color: #e74c3c;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        z-index: 10;
    }
    
    .double-tap-overlay.show {
        opacity: 1;
    }
    
    .artwork-info {
        padding: 1rem;
        border-top: 1px solid #eee;
    }
    
    .artwork-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .artwork-artist {
        font-size: 1rem;
        color: #7f8c8d;
        font-style: italic;
        margin-bottom: 1rem;
    }
    
    .artwork-metadata {
        font-size: 0.9rem;
        color: #95a5a6;
        line-height: 1.4;
    }
    
    .navigation-buttons {
        display: flex;
        justify-content: space-between;
        padding: 1rem;
        background: white;
        border-top: 1px solid #eee;
    }
    
    .nav-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .like-button {
        background: linear-gradient(45deg, #e74c3c, #c0392b);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        transition: all 0.3s ease;
    }
    
    .like-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
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
        margin: 2rem auto;
        max-width: 600px;
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
    
    .stats-mini {
        display: flex;
        justify-content: space-around;
        padding: 0.5rem;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 0.8rem;
    }
    
    /* Hide sidebar by default for mobile-like experience */
    .css-1d391kg {
        display: none;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a6fd8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_artwork' not in st.session_state:
    st.session_state.current_artwork = None
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = ['all']
if 'artwork_history' not in st.session_state:
    st.session_state.artwork_history = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = -1

# Check if user is logged in
if not is_logged_in():
    render_login_page()
    st.stop()

# User is logged in - show main app
current_user = get_current_user()
username = st.session_state.get('username', 'User')

# Main header
st.markdown('<h1 class="main-header">🎨 Art Explorer</h1>', unsafe_allow_html=True)

# User info section
st.markdown(f"""
<div class="user-info">
    <h3>Welcome, {username}! 👋</h3>
    <p>Double-tap to like • Swipe to explore</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with filters and navigation
with st.sidebar:
    st.subheader("🔍 Filter Sources")
    
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
        st.session_state.current_artwork = None
        st.session_state.artwork_history = []
        st.session_state.current_index = -1
    
    st.markdown("---")
    st.subheader("📊 Your Stats")
    
    # Get user-specific stats
    user_stats = get_user_stats(current_user)
    
    st.metric("Liked Artworks", user_stats['liked_artworks'])
    st.metric("Museums", user_stats['unique_museums'])
    st.metric("Total Interactions", user_stats['total_artworks'])
    
    st.markdown("---")
    st.subheader("🖼️ Navigation")
    
    if st.button("🎨 View Gallery", help="Go to your gallery page"):
        st.switch_page("pages/1_gallery.py")
    
    if st.button("🚪 Logout", help="Logout from your account"):
        logout_user()
        st.success("Logged out successfully!")
        st.rerun()

# Main content area - Instagram-style layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Get New Artwork Button
    if st.button("🎲 Start Exploring", key="new_artwork_btn", help="Start exploring artworks"):
        with st.spinner("Loading artworks..."):
            if 'all' in st.session_state.selected_sources:
                artwork = fetch_random_artwork(set())
            else:
                artwork = fetch_artworks_from_sources(st.session_state.selected_sources, set())
                if artwork and isinstance(artwork, list):
                    artwork = artwork[0] if artwork else None
            
            if artwork:
                st.session_state.artwork_history = [artwork]
                st.session_state.current_index = 0
                st.session_state.current_artwork = artwork
                st.success("Artworks loaded!")
            else:
                st.error("No artwork found. Try different sources or check your internet connection.")

    # Display current artwork in Instagram style
    if st.session_state.current_artwork:
        artwork = st.session_state.current_artwork
        
        st.markdown('<div class="instagram-container">', unsafe_allow_html=True)
        
        # Artwork header (like Instagram post header)
        st.markdown(f"""
        <div class="artwork-header">
            <div class="artwork-source">{artwork.get('source', 'Unknown Museum')}</div>
            <div style="color: #7f8c8d; font-size: 0.9rem;">🎨</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Artwork image with double-tap functionality
        if artwork.get('image_url'):
            # Create a container for the image with click handling
            st.markdown(f"""
            <div class="artwork-image-container" onclick="handleDoubleTap()">
                <img src="{artwork.get('image_url', '')}" class="artwork-image" alt="{artwork.get('title', 'Artwork')}" />
                <div class="double-tap-overlay" id="heart-overlay">❤️</div>
            </div>
            """, unsafe_allow_html=True)
            
            # JavaScript for double-tap functionality
            st.markdown("""
            <script>
            let lastTap = 0;
            let tapCount = 0;
            
            function handleDoubleTap() {
                const now = Date.now();
                const timeDiff = now - lastTap;
                
                if (timeDiff < 500 && timeDiff > 0) {
                    // Double tap detected
                    const overlay = document.getElementById('heart-overlay');
                    overlay.classList.add('show');
                    
                    // Send like to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: 'like'
                    }, '*');
                    
                    setTimeout(() => {
                        overlay.classList.remove('show');
                    }, 1000);
                }
                
                lastTap = now;
            }
            </script>
            """, unsafe_allow_html=True)
        
        # Artwork info (like Instagram caption)
        st.markdown(f"""
        <div class="artwork-info">
            <div class="artwork-title">{artwork.get('title', 'Untitled')}</div>
            <div class="artwork-artist">by {artwork.get('artist', 'Unknown Artist')}</div>
            <div class="artwork-metadata">
                📅 {artwork.get('date', 'Unknown date')} • 🌍 {artwork.get('origin', 'Unknown origin')} • 🏛️ {artwork.get('department', 'Unknown department')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation buttons (like Instagram actions)
        st.markdown('<div class="navigation-buttons">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Previous", key="prev_btn", help="Go to previous artwork"):
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    st.session_state.current_artwork = st.session_state.artwork_history[st.session_state.current_index]
                    st.rerun()
        
        with col2:
            if st.button("❤️ Like", key="like_btn", help="Like this artwork"):
                if st.session_state.current_artwork:
                    save_feedback(st.session_state.current_artwork, "like", user_id=current_user)
                    st.success("❤️ Liked!")
        
        with col3:
            if st.button("➡️ Next", key="next_btn", help="Go to next artwork"):
                # Load new artwork
                with st.spinner("Loading next artwork..."):
                    if 'all' in st.session_state.selected_sources:
                        new_artwork = fetch_random_artwork(set())
                    else:
                        new_artwork = fetch_artworks_from_sources(st.session_state.selected_sources, set())
                        if new_artwork and isinstance(new_artwork, list):
                            new_artwork = new_artwork[0] if new_artwork else None
                    
                    if new_artwork:
                        st.session_state.artwork_history.append(new_artwork)
                        st.session_state.current_index += 1
                        st.session_state.current_artwork = new_artwork
                        st.rerun()
                    else:
                        st.error("No more artworks found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mini stats below the post
        st.markdown(f"""
        <div class="stats-mini">
            <div class="stat-item">
                <div class="stat-value">{user_stats['liked_artworks']}</div>
                <div class="stat-label">Liked</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{user_stats['unique_museums']}</div>
                <div class="stat-label">Museums</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{user_stats['total_artworks']}</div>
                <div class="stat-label">Viewed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Empty state with prominent call-to-action
        st.markdown("""
        <div class="empty-state">
            <h2>🎨 Ready to Explore Art?</h2>
            <p>Click "Start Exploring" to begin your Instagram-style art journey.</p>
            <p>Double-tap images to like • Use navigation buttons to browse</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    🎨 Art Explorer | Instagram-Style Art Discovery
</div>
""", unsafe_allow_html=True)