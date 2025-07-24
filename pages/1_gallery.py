import streamlit as st
from utils import load_feedback_df, save_feedback, clear_feedback_csv

st.title("🖼️ Your Liked Artworks")

def reload_feedback_df():
    df = load_feedback_df()
    if not df.empty and "liked" in df.columns:
        # Normalize liked column to boolean True/False
        df["liked"] = df["liked"].astype(str).str.lower().map({
            "true": True,
            "false": False,
            "like": True,
            "dislike": False
        }).fillna(False)
    return df

# Always reload fresh feedback DataFrame on every run — do NOT cache in session_state
df = reload_feedback_df()

if df.empty or not df["liked"].any():
    st.info("No liked artworks yet. Start liking paintings from the main page!")
else:
    liked_df = df[df["liked"]].copy()

    # Initialize or update notes and ratings only if liked artworks count changed
    if "liked_count" not in st.session_state or st.session_state.liked_count != len(liked_df):
        st.session_state.liked_count = len(liked_df)
        st.session_state.notes = {row.image_url: row.get("notes", "") for _, row in liked_df.iterrows()}
        st.session_state.ratings = {row.image_url: int(row.get("rating", 3)) for _, row in liked_df.iterrows()}

    st.write(f"### You liked {len(liked_df)} artworks.")

    cards_per_row = 3
    rows = (len(liked_df) + cards_per_row - 1) // cards_per_row

    for row_idx in range(rows):
        cols = st.columns(cards_per_row)
        for col_idx in range(cards_per_row):
            idx = row_idx * cards_per_row + col_idx
            if idx >= len(liked_df):
                break

            art = liked_df.iloc[idx]
            image_url = art["image_url"]
            title = art["title"]
            artist = art["artist"]

            with cols[col_idx]:
                # Card styling
                st.markdown(
                    f"""
                    <div style="
                        border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:20px; 
                        box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
                        ">
                        <img src="{image_url}" alt="{title}" style="width:100%; height:200px; object-fit:cover; border-radius:8px"/>
                        <h4 style="margin: 10px 0 2px 0; font-weight: 600;">{title}</h4>
                        <p style="margin: 0; color: #555; font-style: italic;">{artist}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

                # Toggle button with single click toggling
                toggle_key = f"show_details_{image_url}"
                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = False
                
                if st.button(
                    "Hide Details" if st.session_state[toggle_key] else "Show Details",
                    key=f"toggle_{image_url}"
                ):
                    st.session_state[toggle_key] = not st.session_state[toggle_key]

                if st.session_state[toggle_key]:
                    st.markdown(f"**Date:** {art['date']}")
                    st.markdown(f"**Origin:** {art['origin']}")
                    st.markdown(f"**Department:** {art['department']}")
                    st.markdown(f"**Gallery:** {art['source']}")

                    note_key = f"note_{image_url}"
                    note = st.text_area("Your notes", value=st.session_state.notes.get(image_url, ""), key=note_key)
                    st.session_state.notes[image_url] = note

                    rating_key = f"rating_{image_url}"
                    rating_value = st.session_state.ratings.get(image_url, 3)
                    rating_value = min(max(rating_value, 1), 5)

                    rating = st.radio(
                        "Rating (1-5 stars)",
                        options=[1, 2, 3, 4, 5],
                        index=rating_value - 1,
                        key=rating_key,
                        format_func=lambda x: "⭐" * x
                    )
                    st.session_state.ratings[image_url] = rating

    if st.button("💾 Save Notes & Ratings", key="save_notes_ratings"):
        for _, art in liked_df.iterrows():
            save_feedback({
                "title": art["title"],
                "image_url": art["image_url"],
                "artist": art["artist"],
                "date": art["date"],
                "origin": art["origin"],
                "department": art["department"],
                "source": art["source"],
                "notes": st.session_state.notes.get(art["image_url"], ""),
                "rating": st.session_state.ratings.get(art["image_url"], 3),
            }, "like", overwrite=True)
        st.success("Notes and ratings saved!")
        # After saving, rerun to reload fresh data
        st.rerun()

    st.write("---")
    st.write("### Export Liked Artworks")

    csv_data = liked_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_data, file_name="liked_artworks.csv", mime="text/csv")

    json_data = liked_df.to_json(orient="records", indent=2).encode("utf-8")
    st.download_button("Download JSON", json_data, file_name="liked_artworks.json", mime="application/json")

    st.write("---")
    st.write("### Reset Feedback History")

    confirm_clear = st.checkbox("I understand this will clear all feedback (likes, dislikes, notes, ratings).", key="confirm_clear")
    if confirm_clear:
        if st.button("⚠️ Clear All Feedback", key="clear_feedback"):
            clear_feedback_csv()
            for key in list(st.session_state.keys()):
                if key.startswith("note_") or key.startswith("rating_") or key.startswith("show_details_"):
                    del st.session_state[key]
            if "notes" in st.session_state:
                del st.session_state.notes
            if "ratings" in st.session_state:
                del st.session_state.ratings
            if "liked_count" in st.session_state:
                del st.session_state.liked_count
            st.success("Feedback history cleared.")
            st.rerun()