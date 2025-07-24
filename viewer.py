import streamlit as st
from art_sources import fetch_random_artwork
from utils import load_seen_urls, save_feedback

def show_viewer():
    st.title("🎨 Art Viewer")

    seen_urls = load_seen_urls()

    art = fetch_random_artwork(seen_urls)
    if not art:
        st.error("⚠️ Could not fetch artwork. Try again later.")
        return

    st.image(art["image_url"], use_column_width=True)
    st.markdown(f"### {art['title']}")
    st.markdown(f"*{art['artist']}* | {art['date']} | {art['origin']} | {art['source']}")

    col1, col2 = st.columns(2)
    if col1.button("👍 Like"):
        save_feedback(art, liked=True)
        st.rerun()
    if col2.button("👎 Dislike"):
        save_feedback(art, liked=False)
        st.rerun()