import streamlit as st
from art_sources import fetch_random_artwork
from utils import load_seen_urls, save_feedback

st.set_page_config(page_title="Art Explorer", layout="centered")
st.title("🎨 Do You Like This Painting?")

def reload_seen_urls():
    # Re-load seen URLs fresh from saved feedback CSV or DB
    return load_seen_urls()

# Always reload seen_urls at start of script (not only on first load)
st.session_state.seen_urls = reload_seen_urls()

if "like_count" not in st.session_state:
    st.session_state.like_count = 0
if "dislike_count" not in st.session_state:
    st.session_state.dislike_count = 0

# On first load or after feedback, fetch art excluding seen URLs
if "art" not in st.session_state or st.session_state.art is None:
    st.session_state.art = fetch_random_artwork(st.session_state.seen_urls)

def show_counters():
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; gap: 50px; font-size: 20px; margin-bottom: 15px;">
            <div style="color: green;">👍 Likes: {st.session_state.like_count}</div>
            <div style="color: red;">👎 Dislikes: {st.session_state.dislike_count}</div>
        </div>
        """, 
        unsafe_allow_html=True,
    )

def show_artwork(art):
    st.image(art['image_url'], caption=art['title'], use_container_width=True)
    st.markdown(f"**Artist:** {art['artist']}")
    st.markdown(f"**Date:** {art['date']}")
    st.markdown(f"**Place of Origin:** {art['origin']}")
    st.markdown(f"**Department:** {art['department']}")
    st.markdown(f"**Gallery:** {art['source']}")

def handle_feedback(liked):
    if liked:
        st.session_state.like_count += 1
    else:
        st.session_state.dislike_count += 1

    # Save feedback first - ensure this writes immediately
    save_feedback(st.session_state.art, liked=liked)

    # Reload seen URLs fresh from saved feedback (includes current art)
    st.session_state.seen_urls = reload_seen_urls()

    # Fetch next artwork excluding all seen URLs
    next_art = fetch_random_artwork(st.session_state.seen_urls)
    if next_art:
        st.session_state.art = next_art
    else:
        st.session_state.art = None

    # Refresh UI to show next artwork
    st.rerun()

if st.session_state.art:
    show_counters()
    show_artwork(st.session_state.art)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Like", use_container_width=True):
            handle_feedback(True)
    with col2:
        if st.button("👎 Dislike", use_container_width=True):
            handle_feedback(False)
else:
    show_counters()
    st.error("⚠️ No more new artworks available!")