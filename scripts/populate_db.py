#!/usr/bin/env python3
"""
Populate database with sample artworks for testing
"""

from database.config import SessionLocal
from database.models import Artwork
from datetime import datetime

def populate_sample_artworks():
    """Add sample artworks to the database"""
    db = SessionLocal()
    
    try:
        # Sample artworks from different sources
        sample_artworks = [
            {
                "title": "The Starry Night",
                "artist": "Vincent van Gogh",
                "date": "1889",
                "origin": "Netherlands",
                "department": "Post-Impressionism",
                "source": "Metropolitan Museum of Art",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
                "external_id": "sample_001"
            },
            {
                "title": "Mona Lisa",
                "artist": "Leonardo da Vinci",
                "date": "1503-1519",
                "origin": "Italy",
                "department": "Renaissance",
                "source": "Louvre Museum",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/687px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
                "external_id": "sample_002"
            },
            {
                "title": "The Persistence of Memory",
                "artist": "Salvador Dalí",
                "date": "1931",
                "origin": "Spain",
                "department": "Surrealism",
                "source": "Museum of Modern Art",
                "image_url": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
                "external_id": "sample_003"
            },
            {
                "title": "The Scream",
                "artist": "Edvard Munch",
                "date": "1893",
                "origin": "Norway",
                "department": "Expressionism",
                "source": "National Gallery of Norway",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
                "external_id": "sample_004"
            },
            {
                "title": "Girl with a Pearl Earring",
                "artist": "Johannes Vermeer",
                "date": "1665",
                "origin": "Netherlands",
                "department": "Dutch Golden Age",
                "source": "Mauritshuis",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg",
                "external_id": "sample_005"
            },
            {
                "title": "The Night Watch",
                "artist": "Rembrandt van Rijn",
                "date": "1642",
                "origin": "Netherlands",
                "department": "Dutch Golden Age",
                "source": "Rijksmuseum",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Rembrandt_van_Rijn_-_De_Nachtwacht_-_Google_Art_Project.jpg/1280px-Rembrandt_van_Rijn_-_De_Nachtwacht_-_Google_Art_Project.jpg",
                "external_id": "sample_006"
            },
            {
                "title": "American Gothic",
                "artist": "Grant Wood",
                "date": "1930",
                "origin": "United States",
                "department": "Regionalism",
                "source": "Art Institute of Chicago",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg/1280px-Grant_Wood_-_American_Gothic_-_Google_Art_Project.jpg",
                "external_id": "sample_007"
            },
            {
                "title": "The Birth of Venus",
                "artist": "Sandro Botticelli",
                "date": "1485",
                "origin": "Italy",
                "department": "Renaissance",
                "source": "Uffizi Gallery",
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project.jpg/1280px-Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project.jpg",
                "external_id": "sample_008"
            }
        ]
        
        # Check if artworks already exist
        existing_count = db.query(Artwork).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} artworks. Skipping population.")
            return
        
        # Add sample artworks
        for artwork_data in sample_artworks:
            artwork = Artwork(**artwork_data)
            db.add(artwork)
        
        db.commit()
        print(f"✅ Added {len(sample_artworks)} sample artworks to database")
        
        # Verify
        total_count = db.query(Artwork).count()
        print(f"Total artworks in database: {total_count}")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🎨 Populating database with sample artworks...")
    populate_sample_artworks() 