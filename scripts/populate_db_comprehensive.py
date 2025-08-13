#!/usr/bin/env python3
"""
Comprehensive database population script for Art Explorer
Fetches artworks from multiple museum APIs and populates the database
"""

import os
import sys
import requests
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append('.')

from database.config import SessionLocal, engine
from database.models import Base, Artwork
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Museum API configurations
MUSEUM_APIS = {
    'met': {
        'base_url': 'https://collectionapi.metmuseum.org/public/collection/v1',
        'enabled': True,
        'max_artworks': 50
    },
    'smithsonian': {
        'base_url': 'https://api.si.edu/openaccess/api/v1.0',
        'enabled': True,
        'max_artworks': 30,
        'api_key': os.getenv('SMITHSONIAN_API_KEY')
    },
    'harvard': {
        'base_url': 'https://api.harvardartmuseums.org/object',
        'enabled': True,
        'max_artworks': 30,
        'api_key': os.getenv('HARVARD_API_KEY')
    },
    'cleveland': {
        'base_url': 'https://openaccess-api.clevelandart.org/api/v1',
        'enabled': True,
        'max_artworks': 30
    },
    'chicago': {
        'base_url': 'https://api.artic.edu/api/v1',
        'enabled': True,
        'max_artworks': 30
    },
    'walters': {
        'base_url': 'https://api.thewalters.org/v1',
        'enabled': True,
        'max_artworks': 20
    }
}

def setup_database():
    """Initialize the database and create all tables"""
    print("🚀 Setting up Art Explorer Database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    return True

def fetch_met_artworks(max_count=50):
    """Fetch artworks from The Metropolitan Museum of Art"""
    print(f"🎨 Fetching up to {max_count} artworks from The Met...")
    artworks = []
    
    try:
        # MET API doesn't support search with GET, so we'll use random object IDs
        object_ranges = [
            (1000, 50000),      # Early objects
            (50000, 150000),    # 19th century
            (150000, 250000),   # Modern
            (250000, 350000),   # Contemporary
            (350000, 450000),   # Various periods
        ]
        
        attempts = 0
        max_attempts = max_count * 3  # Try more IDs to get enough valid ones
        
        while len(artworks) < max_count and attempts < max_attempts:
            # Pick a random range
            start_range, end_range = random.choice(object_ranges)
            object_id = random.randint(start_range, end_range)
            attempts += 1
            
            try:
                # Fetch object details
                url = f"{MUSEUM_APIS['met']['base_url']}/objects/{object_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract image URL
                    image_url = data.get("primaryImageSmall") or data.get("primaryImage")
                    if not image_url or image_url.lower().endswith(".gif"):
                        continue

                    # Check if object has basic required info
                    title = data.get("title")
                    if not title:
                        continue

                    artwork = {
                        "title": title,
                        "artist": data.get("artistDisplayName", "Unknown"),
                        "date": data.get("objectDate", "Unknown"),
                        "origin": data.get("culture") or data.get("country", "Unknown"),
                        "department": data.get("department", "Unknown"),
                        "image_url": image_url,
                        "source": "met",
                        "external_id": str(object_id)
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                    # Small delay to be respectful to the API
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"  ⚠️  Error fetching object {object_id}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error fetching from Met: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from The Met")
    return artworks

def fetch_smithsonian_artworks(max_count=30):
    """Fetch artworks from Smithsonian Institution"""
    print(f"🏛️ Fetching up to {max_count} artworks from Smithsonian...")
    artworks = []
    
    try:
        # Smithsonian API search for art
        search_params = {
            'q': 'art',
            'type': 'art',
            'api_key': MUSEUM_APIS['smithsonian']['api_key'] or 'demo',
            'rows': min(max_count, 100)
        }
        
        url = f"{MUSEUM_APIS['smithsonian']['base_url']}/search"
        response = requests.get(url, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('response', {}).get('rows', [])
            
            for result in results[:max_count]:
                try:
                    content = result.get('content', {})
                    
                    # Extract basic info
                    title = content.get('title', {}).get('content', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Get image URL if available
                    image_url = None
                    if 'descriptiveNonRepeating' in content:
                        desc = content['descriptiveNonRepeating']
                        if 'online_media' in desc and desc['online_media'].get('media'):
                            media = desc['online_media']['media'][0]
                            image_url = media.get('thumbnail', media.get('content'))
                    
                    artwork = {
                        "title": title,
                        "artist": content.get('freetext', {}).get('name', [{}])[0].get('content', 'Unknown'),
                        "date": content.get('freetext', {}).get('date', [{}])[0].get('content', 'Unknown'),
                        "origin": content.get('freetext', {}).get('place', [{}])[0].get('content', 'Unknown'),
                        "department": content.get('freetext', {}).get('topic', [{}])[0].get('content', 'Unknown'),
                        "image_url": image_url,
                        "source": "smithsonian",
                        "external_id": result.get('id', '')
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing Smithsonian result: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error fetching from Smithsonian: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from Smithsonian")
    return artworks

def fetch_harvard_artworks(max_count=30):
    """Fetch artworks from Harvard Art Museums"""
    print(f"🎓 Fetching up to {max_count} artworks from Harvard...")
    artworks = []
    
    try:
        # Harvard API search for paintings
        search_params = {
            'q': 'painting',
            'apikey': MUSEUM_APIS['harvard']['api_key'] or 'demo',
            'size': min(max_count, 100),
            'hasimage': 1
        }
        
        url = f"{MUSEUM_APIS['harvard']['base_url']}/search"
        response = requests.get(url, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('records', [])
            
            for result in results[:max_count]:
                try:
                    # Extract basic info
                    title = result.get('title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Get image URL
                    image_url = None
                    if 'images' in result and result['images']:
                        image_url = result['images'][0].get('baseimageurl')
                    
                    artwork = {
                        "title": title,
                        "artist": result.get('people', [{}])[0].get('name', 'Unknown') if result.get('people') else 'Unknown',
                        "date": result.get('dated', 'Unknown'),
                        "origin": result.get('culture', 'Unknown'),
                        "department": result.get('classification', 'Unknown'),
                        "image_url": image_url,
                        "source": "harvard",
                        "external_id": str(result.get('id', ''))
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing Harvard result: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error fetching from Harvard: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from Harvard")
    return artworks

def fetch_cleveland_artworks(max_count=30):
    """Fetch artworks from Cleveland Museum of Art"""
    print(f"🏛️ Fetching up to {max_count} artworks from Cleveland...")
    artworks = []
    
    try:
        # Cleveland API search for paintings
        search_params = {
            'q': 'painting',
            'limit': min(max_count, 100),
            'has_image': 1
        }
        
        url = f"{MUSEUM_APIS['cleveland']['base_url']}/artworks/search"
        response = requests.get(url, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', [])
            
            for result in results[:max_count]:
                try:
                    # Extract basic info
                    title = result.get('title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Get image URL
                    image_url = None
                    if 'images' in result and result['images']:
                        image_url = result['images'][0].get('url')
                    
                    artwork = {
                        "title": title,
                        "artist": result.get('creators', [{}])[0].get('description', 'Unknown') if result.get('creators') else 'Unknown',
                        "date": result.get('creation_date', 'Unknown'),
                        "origin": result.get('culture', 'Unknown'),
                        "department": result.get('department', 'Unknown'),
                        "image_url": image_url,
                        "source": "cleveland",
                        "external_id": str(result.get('id', ''))
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing Cleveland result: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error fetching from Cleveland: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from Cleveland")
    return artworks

def fetch_chicago_artworks(max_count=30):
    """Fetch artworks from Art Institute of Chicago"""
    print(f"🏛️ Fetching up to {max_count} artworks from Chicago...")
    artworks = []
    
    try:
        # Chicago API search for paintings
        search_params = {
            'q': 'painting',
            'limit': min(max_count, 100),
            'fields': 'id,title,artist_title,date_display,place_of_origin,department_title,image_id'
        }
        
        url = f"{MUSEUM_APIS['chicago']['base_url']}/artworks/search"
        response = requests.get(url, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('data', [])
            
            for result in results[:max_count]:
                try:
                    # Extract basic info
                    title = result.get('title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Get image URL
                    image_url = None
                    if result.get('image_id'):
                        image_url = f"https://www.artic.edu/iiif/2/{result['image_id']}/full/400,/0/default.jpg"
                    
                    artwork = {
                        "title": title,
                        "artist": result.get('artist_title', 'Unknown'),
                        "date": result.get('date_display', 'Unknown'),
                        "origin": result.get('place_of_origin', 'Unknown'),
                        "department": result.get('department_title', 'Unknown'),
                        "image_url": image_url,
                        "source": "chicago",
                        "external_id": str(result.get('id', ''))
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing Chicago result: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error fetching from Chicago: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from Chicago")
    return artworks

def fetch_walters_artworks(max_count=20):
    """Fetch artworks from Walters Art Museum"""
    print(f"🏛️ Fetching up to {max_count} artworks from Walters...")
    artworks = []
    
    try:
        # Walters API search for paintings
        search_params = {
            'q': 'painting',
            'limit': min(max_count, 100)
        }
        
        url = f"{MUSEUM_APIS['walters']['base_url']}/objects/search"
        response = requests.get(url, params=search_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('Items', [])
            
            for result in results[:max_count]:
                try:
                    # Extract basic info
                    title = result.get('Title', 'Unknown Title')
                    if not title or title == 'Unknown Title':
                        continue
                    
                    # Get image URL
                    image_url = None
                    if 'PrimaryImage' in result:
                        image_url = result['PrimaryImage'].get('Raw')
                    
                    artwork = {
                        "title": title,
                        "artist": result.get('Creator', 'Unknown'),
                        "date": result.get('Date', 'Unknown'),
                        "origin": result.get('Culture', 'Unknown'),
                        "department": result.get('Classification', 'Unknown'),
                        "image_url": image_url,
                        "source": "walters",
                        "external_id": str(result.get('ObjectID', ''))
                    }
                    
                    artworks.append(artwork)
                    print(f"  ✅ Added: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing Walters result: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Error fetching from Walters: {e}")
    
    print(f"🎯 Fetched {len(artworks)} artworks from Walters")
    return artworks

def save_artworks_to_db(artworks):
    """Save artworks to the database"""
    if not artworks:
        print("⚠️  No artworks to save")
        return 0
    
    db = SessionLocal()
    saved_count = 0
    
    try:
        for artwork_data in artworks:
            try:
                # Check if artwork already exists
                existing = db.query(Artwork).filter(
                    Artwork.external_id == artwork_data['external_id'],
                    Artwork.source == artwork_data['source']
                ).first()
                
                if existing:
                    print(f"  ⚠️  Skipping duplicate: {artwork_data['title'][:50]}...")
                    continue
                
                # Create new artwork
                artwork = Artwork(**artwork_data)
                db.add(artwork)
                saved_count += 1
                
            except Exception as e:
                print(f"  ❌ Error saving artwork {artwork_data.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"💾 Successfully saved {saved_count} new artworks to database")
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()
    
    return saved_count

def populate_database():
    """Main function to populate the database with artworks"""
    print("🎨 Starting comprehensive database population...")
    print("=" * 60)
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed. Exiting.")
        return
    
    # Check current artwork count
    db = SessionLocal()
    try:
        existing_count = db.query(Artwork).count()
        print(f"📊 Current database has {existing_count} artworks")
    except Exception as e:
        print(f"⚠️  Could not check current count: {e}")
        existing_count = 0
    finally:
        db.close()
    
    if existing_count > 100:
        print("⚠️  Database already has many artworks. Consider if you want to continue.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Population cancelled.")
            return
    
    all_artworks = []
    
    # Fetch from each enabled museum API
    for museum_name, config in MUSEUM_APIS.items():
        if not config['enabled']:
            print(f"⏭️  Skipping {museum_name} (disabled)")
            continue
            
        print(f"\n🌐 Fetching from {museum_name.upper()}...")
        
        try:
            if museum_name == 'met':
                artworks = fetch_met_artworks(config['max_artworks'])
            elif museum_name == 'smithsonian':
                artworks = fetch_smithsonian_artworks(config['max_artworks'])
            elif museum_name == 'harvard':
                artworks = fetch_harvard_artworks(config['max_artworks'])
            elif museum_name == 'cleveland':
                artworks = fetch_cleveland_artworks(config['max_artworks'])
            elif museum_name == 'chicago':
                artworks = fetch_chicago_artworks(config['max_artworks'])
            elif museum_name == 'walters':
                artworks = fetch_walters_artworks(config['max_artworks'])
            else:
                continue
            
            all_artworks.extend(artworks)
            
            # Small delay between museums
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error fetching from {museum_name}: {e}")
            continue
    
    print(f"\n📊 Total artworks fetched: {len(all_artworks)}")
    
    if all_artworks:
        print("\n💾 Saving artworks to database...")
        saved_count = save_artworks_to_db(all_artworks)
        
        # Final count
        db = SessionLocal()
        try:
            final_count = db.query(Artwork).count()
            print(f"\n🎉 Population complete!")
            print(f"📊 Database now contains {final_count} artworks")
            print(f"✨ Added {saved_count} new artworks")
        except Exception as e:
            print(f"⚠️  Could not get final count: {e}")
        finally:
            db.close()
    else:
        print("❌ No artworks were fetched. Database population failed.")

if __name__ == "__main__":
    print("🎨 Art Explorer Comprehensive Database Population")
    print("=" * 60)
    
    try:
        populate_database()
    except KeyboardInterrupt:
        print("\n\n🛑 Population interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)