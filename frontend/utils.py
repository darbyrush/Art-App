import csv
import os
import pandas as pd

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
    """Load full feedback as DataFrame with all columns including notes and rating."""
    if not os.path.exists(FEEDBACK_CSV):
        return pd.DataFrame(columns=FIELDNAMES)
    
    df = pd.read_csv(FEEDBACK_CSV)

    # Ensure all required columns are present
    for col in FIELDNAMES:
        if col not in df.columns:
            default = "" if col not in ["rating"] else 0
            df[col] = default

    # Correct types
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

    return df[FIELDNAMES]

def save_feedback(art, liked, overwrite=False):
    """
    Save feedback about an artwork.
    If overwrite=True, update existing record by image_url; else append.
    """
    new_row = {
        "title": art.get("title", ""),
        "image_url": art.get("image_url", ""),
        "liked": liked,
        "artist": art.get("artist", ""),
        "date": art.get("date", ""),
        "origin": art.get("origin", ""),
        "department": art.get("department", ""),
        "source": art.get("source", ""),
        "notes": art.get("notes", ""),
        "rating": int(art.get("rating", 0))
    }

    # Overwrite logic
    if overwrite and os.path.exists(FEEDBACK_CSV):
        df = pd.read_csv(FEEDBACK_CSV)
        if "image_url" in df.columns:
            idx = df.index[df["image_url"] == new_row["image_url"]]
            if len(idx) > 0:
                df.loc[idx[0]] = new_row
                df.to_csv(FEEDBACK_CSV, index=False)
                return

    # Append logic
    file_exists = os.path.exists(FEEDBACK_CSV)
    with open(FEEDBACK_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_row)

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

def clear_feedback_csv():
    """Delete the feedback CSV entirely."""
    if os.path.exists(FEEDBACK_CSV):
        os.remove(FEEDBACK_CSV)