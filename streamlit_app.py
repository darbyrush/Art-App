#!/usr/bin/env python3
"""
Art Explorer - Main Application
Streamlit app for exploring artworks with Instagram-style interface
"""

import streamlit as st
import pandas as pd
from frontend.api_client import api_client
from frontend.components.auth import is_logged_in, get_current_user, logout_user, render_login_page, require_auth
from app.config import config

# Page configuration
st.set_page_config(**config.PAGE_CONFIG)

# Custom CSS for Instagram-style design
st.markdown(config.get_css_styles(), unsafe_allow_html=True)

# Initialize session state
for key, default_value in config.SESSION_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Global authentication check
require_auth()

# Get current user
current_user = get_current_user()
username = st.session_state.get('username', 'User')

# Sidebar
with st.sidebar:
    st.title("🎨 Art Explorer")
    
    # User info
    if st.session_state.get('access_token'):
        st.success(f"✅ Logged in as: {username}")
        
        # Logout button
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # Source filters
    st.subheader("🏛️ Museum Sources")
    selected_sources = st.multiselect(
        "Select museums to explore:",
        options=config.AVAILABLE_SOURCES,
        default=config.DEFAULT_SOURCES,
        key="selected_sources"
    )
    
    # Stats section
    if st.session_state.get('access_token'):
        try:
            stats = api_client.get_user_stats()
            st.subheader("📊 Your Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Liked Artworks", stats.get('liked_artworks', 0))
            with col2:
                st.metric("Museums", stats.get('unique_museums', 0))
        except Exception as e:
            st.error(f"Error loading stats: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area - Instagram-style layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Check if user is authenticated
    if not st.session_state.get('access_token'):
        st.markdown("""
        <div class="empty-state">
            <h2>🔐 Please Log In</h2>
            <p>You need to log in to explore artworks.</p>
            <p>Use the sidebar to register or log in.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Debug: Show authentication status
        st.success(f"✅ Logged in as: {st.session_state.get('username', 'User')}")
        
        # Debug: Show session state info
        with st.expander("🔍 Debug Info"):
            st.write("Session State:")
            st.write(f"- access_token: {'✅ Set' if st.session_state.get('access_token') else '❌ Not set'}")
            st.write(f"- current_artwork: {'✅ Set' if st.session_state.get('current_artwork') else '❌ Not set'}")
            st.write(f"- selected_sources: {selected_sources}")
        
        # Check if we already have an artwork loaded
        if not st.session_state.get('current_artwork'):
            st.markdown("""
            <div class="empty-state">
                <h2>🎨 Welcome to Art Explorer!</h2>
                <p>Ready to discover amazing artworks? Click the button below to start exploring!</p>
                <p><em>You can select specific museums from the sidebar filters above.</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Get New Artwork Button
        if st.button("🎲 Start Exploring", key="new_artwork_btn", help="Start exploring artworks"):
            with st.spinner("Loading artworks..."):
                try:
                    # Check if user is authenticated
                    if not st.session_state.get('access_token'):
                        st.error("Please log in first to explore artworks.")
                        st.stop()
                    
                    artwork = api_client.get_random_artwork(selected_sources)
                    
                    if artwork:
                        st.session_state.artwork_history = [artwork]
                        st.session_state.current_index = 0
                        st.session_state.current_artwork = artwork
                        st.success("🎨 Artwork loaded successfully!")
                        st.rerun()  # Refresh the page to show the artwork
                    else:
                        st.error("❌ No artwork found. Try different sources or check your internet connection.")
                        st.info("💡 Make sure you're logged in and the API is running.")
                except Exception as e:
                    st.error(f"Error loading artwork: {e}")
                    st.error("Please make sure you are logged in and try again.")

    # Display current artwork in Instagram style
    if st.session_state.get('current_artwork'):
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
            st.markdown(config.get_double_tap_js(), unsafe_allow_html=True)
        
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
                    try:
                        success = api_client.like_artwork(artwork['id'], True)
                        if success:
                            st.success("❤️ Liked!")
                        else:
                            st.error("Failed to like artwork")
                    except Exception as e:
                        st.error(f"Error liking artwork: {e}")
        
        with col3:
            if st.button("➡️ Next", key="next_btn", help="Go to next artwork"):
                # Load new artwork
                with st.spinner("Loading next artwork..."):
                    try:
                        new_artwork = api_client.get_random_artwork(selected_sources)
                        
                        if new_artwork:
                            st.session_state.artwork_history.append(new_artwork)
                            st.session_state.current_index += 1
                            st.session_state.current_artwork = new_artwork
                            st.rerun()
                        else:
                            st.error("No more artworks found.")
                    except Exception as e:
                        st.error(f"Error loading next artwork: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True) 