import streamlit as st
import pandas as pd
from frontend.utils import load_feedback_df, save_feedback, clear_feedback_csv
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="Art Gallery",
    page_icon="🖼️",
    layout="wide"
)

# Custom CSS for cool coordinated cards
st.markdown("""
<style>
    .gallery-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .filter-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        color: white;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
    }
    
    .artwork-card {
        border-radius: 15px;
        padding: 0;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        overflow: hidden;
        transition: transform 0.3s ease;
    }
    
    .artwork-card:hover {
        transform: translateY(-5px);
    }
    
    .card-header {
        padding: 1rem;
        color: white;
        font-weight: bold;
    }
    
    .card-body {
        padding: 1rem;
        background: white;
    }
    
    .card-footer {
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.9);
        border-top: 1px solid #eee;
    }
    
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    
    .rating-stars {
        color: #ffd700;
        font-size: 1.2rem;
    }
    
    .filter-section {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="gallery-header">🖼️ Your Art Gallery</h1>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_gallery_data():
    df = load_feedback_df()
    if not df.empty and "liked" in df.columns:
        df["liked"] = df["liked"].astype(str).str.lower().map({
            "true": True, "false": False, "like": True, "dislike": False
        }).fillna(False)
        return df[df["liked"]].copy()
    return pd.DataFrame()

liked_df = load_gallery_data()

if liked_df.empty:
    st.info("🎨 No liked artworks yet. Start exploring art from the main page!")
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h3>Your gallery is empty</h3>
        <p>Go back to the main page and start liking some artworks!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Gallery statistics
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Artworks", len(liked_df))
    
    with col2:
        unique_sources = liked_df['source'].nunique()
        st.metric("Museums", unique_sources)
    
    with col3:
        if 'rating' in liked_df.columns:
            # Handle non-numeric values in rating column
            rating_series = pd.to_numeric(liked_df['rating'], errors='coerce')
            avg_rating = rating_series.mean()
            if pd.isna(avg_rating):
                avg_rating = 0
        else:
            avg_rating = 0
        st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
    
    with col4:
        if 'notes' in liked_df.columns:
            # Convert to string and handle NaN values
            notes_series = liked_df['notes'].astype(str).replace('nan', '')
            total_notes = notes_series.str.len().sum()
        else:
            total_notes = 0
        st.metric("Total Notes", f"{total_notes} chars")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtering section
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.subheader("🔍 Filter Your Gallery")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Source filter
        sources = ['All'] + sorted(liked_df['source'].unique().tolist())
        selected_source = st.selectbox("Museum/Source", sources)
    
    with col2:
        # Date filter
        if 'date' in liked_df.columns:
            # Extract years from date column
            def extract_year(date_str):
                if pd.isna(date_str) or date_str == 'Unknown':
                    return None
                # Try to extract year from various formats
                year_match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', str(date_str))
                return int(year_match.group()) if year_match else None
            
            liked_df['year'] = liked_df['date'].apply(extract_year)
            years = ['All'] + sorted([str(y) for y in liked_df['year'].dropna().unique() if y is not None])
            selected_year = st.selectbox("Time Period", years)
        else:
            selected_year = 'All'
    
    with col3:
        # Artist filter
        # Handle mixed data types in artist column
        artist_values = liked_df['artist'].dropna().unique()
        artist_strings = [str(artist) for artist in artist_values if str(artist) != 'nan']
        artists = ['All'] + sorted(artist_strings)
        selected_artist = st.selectbox("Artist", artists)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = liked_df.copy()
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    
    if selected_year != 'All':
        filtered_df = filtered_df[filtered_df['year'] == int(selected_year)]
    
    if selected_artist != 'All':
        filtered_df = filtered_df[filtered_df['artist'] == selected_artist]
    
    # Show filtered results
    st.write(f"**Showing {len(filtered_df)} artworks**")
    
    # Color schemes for different sources
    color_schemes = {
        'Cleveland Museum of Art': {'header': '#e74c3c', 'body': '#fdf2f2'},
        'Metropolitan Museum of Art': {'header': '#3498db', 'body': '#f0f8ff'},
        'Art Institute of Chicago': {'header': '#2ecc71', 'body': '#f0fff4'},
        'Walters Art Museum': {'header': '#9b59b6', 'body': '#f8f4ff'},
        'National Gallery of Art': {'header': '#f39c12', 'body': '#fff8f0'},
        'Smithsonian American Art Museum': {'header': '#e67e22', 'body': '#fff5f0'},
        'Harvard Art Museums': {'header': '#1abc9c', 'body': '#f0fffd'},
        'Unknown': {'header': '#95a5a6', 'body': '#f8f9fa'}
    }
    
    # Display artworks in a grid
    if not filtered_df.empty:
        # Create columns for grid layout
        cols = st.columns(3)
        
        for idx, (_, artwork) in enumerate(filtered_df.iterrows()):
            col_idx = idx % 3
            source = artwork.get('source', 'Unknown')
            color_scheme = color_schemes.get(source, color_schemes['Unknown'])
            
            with cols[col_idx]:
                # Create artwork card
                st.markdown(f"""
                <div class="artwork-card">
                    <div class="card-header" style="background: {color_scheme['header']};">
                        <h4 style="margin: 0; font-size: 1.1rem;">{artwork.get('title', 'Untitled')}</h4>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">{artwork.get('artist', 'Unknown Artist')}</p>
                    </div>
                    <div class="card-body" style="background: {color_scheme['body']};">
                                                        <img src="{artwork.get('image_url', '')}" alt="{artwork.get('title', 'Artwork')}" 
                                     style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px;" onerror="this.style.display='none';"/>
                    </div>
                    <div class="card-footer">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="source-badge" style="background: {color_scheme['header']};">
                                {source}
                            </span>
                            <span class="rating-stars">
                                {'⭐' * int(pd.to_numeric(artwork.get('rating', 0), errors='coerce') or 0)}
                            </span>
                        </div>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #666;">
                            {artwork.get('date', 'Unknown date')}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add expandable details
                with st.expander(f"📋 Details & Notes - {artwork.get('title', 'Untitled')[:20]}"):
                    st.write(f"**Date:** {artwork.get('date', 'Unknown')}")
                    st.write(f"**Origin:** {artwork.get('origin', 'Unknown')}")
                    st.write(f"**Department:** {artwork.get('department', 'Unknown')}")
                    
                    # Notes section
                    current_notes = artwork.get('notes', '')
                    new_notes = st.text_area("Your notes", value=current_notes, key=f"notes_{idx}")
                    
                    # Rating section
                    current_rating = int(pd.to_numeric(artwork.get('rating', 0), errors='coerce') or 0)
                    new_rating = st.slider("Rating", 1, 5, current_rating, key=f"rating_{idx}")
                    
                    # Save button
                    if st.button("💾 Save Changes", key=f"save_{idx}"):
                        # Update the artwork data
                        artwork_data = {
                            'title': artwork.get('title', ''),
                            'image_url': artwork.get('image_url', ''),
                            'artist': artwork.get('artist', ''),
                            'date': artwork.get('date', ''),
                            'origin': artwork.get('origin', ''),
                            'department': artwork.get('department', ''),
                            'source': artwork.get('source', ''),
                            'notes': new_notes,
                            'rating': new_rating,
                        }
                        save_feedback(artwork_data, "like", overwrite=True)
                        st.success("Changes saved!")
                        st.rerun()
    
    # Analytics section
    st.markdown("---")
    st.subheader("📊 Gallery Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Source distribution
        source_counts = liked_df['source'].value_counts()
        fig_source = px.pie(
            values=source_counts.values, 
            names=source_counts.index,
            title="Artworks by Museum"
        )
        st.plotly_chart(fig_source, use_container_width=True)
    
    with col2:
        # Rating distribution
        if 'rating' in liked_df.columns:
            rating_counts = liked_df['rating'].value_counts().sort_index()
            fig_rating = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                title="Rating Distribution",
                labels={'x': 'Rating', 'y': 'Count'}
            )
            st.plotly_chart(fig_rating, use_container_width=True)
    
    # Export section
    st.markdown("---")
    st.subheader("📤 Export Your Gallery")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📄 Download CSV", 
            csv_data, 
            file_name="my_art_gallery.csv", 
            mime="text/csv"
        )
    
    with col2:
        json_data = filtered_df.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button(
            "📄 Download JSON", 
            json_data, 
            file_name="my_art_gallery.json", 
            mime="application/json"
        )
    
    # Clear gallery section
    st.markdown("---")
    st.subheader("🗑️ Gallery Management")
    
    confirm_clear = st.checkbox("I understand this will clear all my liked artworks and notes.")
    if confirm_clear:
        if st.button("⚠️ Clear All Gallery Items", type="secondary"):
            clear_feedback_csv()
            st.success("Gallery cleared successfully!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem;">
    🎨 Your Personal Art Gallery | Filter, Organize, and Enjoy Your Collection
</div>
""", unsafe_allow_html=True) 