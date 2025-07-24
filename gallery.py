import streamlit as st
from utils import load_liked_artworks

def show_gallery():
    st.title("🎨 Gallery of Liked Artworks")

    artworks = load_liked_artworks()

    if not artworks:
        st.info("No liked artworks yet. Go discover some!")
        return

    cols = st.columns(3)
    for idx, art in enumerate(artworks):
        with cols[idx % 3]:
            st.image(art["image_url"], use_column_width=True)
            st.markdown(f"**{art['title']}**")
            st.markdown(f"*{art['artist']}*")
            st.caption(f"{art['date']} · {art['origin']} · {art['source']}")