import csv
import os
import pandas as pd
import json
from datetime import datetime

FEEDBACK_CSV = "feedback.csv"
FIELDNAMES = [
    "title", "image_url", "liked", "artist", "date",
    "origin", "department", "source", "notes", "rating"
]

def load_seen_urls():
    """Load seen image URLs from feedback.csv"""
    if not os.path.exists(FEEDBACK_CSV):
        return set()
    df = pd.read_csv(FEEDBACK_CSV)
    return set(df["image_url"].dropna().unique())

def load_feedback_df():
    """Load feedback data from CSV file"""
    if os.path.exists('feedback.csv'):
        try:
            df = pd.read_csv('feedback.csv')
            return df
        except Exception as e:
            print(f"Error loading feedback.csv: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_feedback(artwork_data, rating, notes="", user_id=None):
    """Save feedback to CSV with user ID"""
    df = load_feedback_df()
    
    # Add user_id column if it doesn't exist
    if 'user_id' not in df.columns:
        df['user_id'] = None
    
    # Create new feedback entry
    new_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'title': artwork_data.get('title', ''),
        'image_url': artwork_data.get('image_url', ''),
        'artist': artwork_data.get('artist', ''),
        'date': artwork_data.get('date', ''),
        'origin': artwork_data.get('origin', ''),
        'department': artwork_data.get('department', ''),
        'source': artwork_data.get('source', ''),
        'rating': rating,
        'notes': notes,
        'liked': rating == 'like'
    }
    
    # Add to dataframe
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Save to CSV
    df.to_csv('feedback.csv', index=False)
    return True

def get_user_feedback(user_id):
    """Get feedback data for a specific user"""
    df = load_feedback_df()
    if 'user_id' in df.columns:
        return df[df['user_id'] == user_id].copy()
    return pd.DataFrame()

def get_user_liked_artworks(user_id):
    """Get liked artworks for a specific user"""
    df = get_user_feedback(user_id)
    if not df.empty and "liked" in df.columns:
        df["liked"] = df["liked"].astype(str).str.lower().map({
            "true": True, "false": False, "like": True, "dislike": False
        }).fillna(False)
        return df[df["liked"]].copy()
    return pd.DataFrame()

def update_user_artwork_rating(user_id, artwork_title, new_rating, new_notes=""):
    """Update rating and notes for a specific user's artwork"""
    df = load_feedback_df()
    if 'user_id' in df.columns:
        # Find the specific artwork for this user
        mask = (df['user_id'] == user_id) & (df['title'] == artwork_title)
        if mask.any():
            df.loc[mask, 'rating'] = new_rating
            df.loc[mask, 'notes'] = new_notes
            df.loc[mask, 'liked'] = (new_rating == 'like')
            df.to_csv('feedback.csv', index=False)
            return True
    return False

def clear_user_feedback(user_id):
    """Clear all feedback for a specific user"""
    df = load_feedback_df()
    if 'user_id' in df.columns:
        df = df[df['user_id'] != user_id]
        df.to_csv('feedback.csv', index=False)
        return True
    return False

def clear_feedback_csv():
    """Clear all feedback data"""
    if os.path.exists('feedback.csv'):
        os.remove('feedback.csv')
        return True
    return False

def get_user_stats(user_id):
    """Get statistics for a specific user"""
    df = get_user_feedback(user_id)
    if df.empty:
        return {
            'total_artworks': 0,
            'liked_artworks': 0,
            'unique_museums': 0,
            'avg_rating': 0
        }
    
    liked_df = df[df['liked'] == True] if 'liked' in df.columns else df
    
    # Handle rating calculation safely
    avg_rating = 0
    if 'rating' in liked_df.columns and not liked_df.empty:
        # Convert rating to numeric, handling string values
        try:
            # First try to convert to numeric
            numeric_ratings = pd.to_numeric(liked_df['rating'], errors='coerce')
            # Calculate mean of valid numeric ratings
            valid_ratings = numeric_ratings.dropna()
            if not valid_ratings.empty:
                avg_rating = valid_ratings.mean()
        except:
            # If conversion fails, default to 0
            avg_rating = 0
    
    return {
        'total_artworks': len(df),
        'liked_artworks': len(liked_df),
        'unique_museums': liked_df['source'].nunique() if not liked_df.empty else 0,
        'avg_rating': avg_rating
    }

def remove_last_feedback():
    """Remove the last feedback row from CSV and return it as a dict."""
    if not os.path.exists(FEEDBACK_CSV):
        return None
    df = pd.read_csv(FEEDBACK_CSV)
    if df.empty:
        return None
    last_row = df.iloc[-1].to_dict()
    df = df.iloc[:-1]
    df.to_csv(FEEDBACK_CSV, index=False)
    return last_row