#!/usr/bin/env python3
"""
Test script to verify the population system works
Tests API connections and fetches a few sample artworks
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from database.config import SessionLocal, init_db
        print("   ✅ Database config imported")
    except Exception as e:
        print(f"   ❌ Database config import failed: {e}")
        return False
    
    try:
        from database.models import Artwork
        print("   ✅ Database models imported")
    except Exception as e:
        print(f"   ❌ Database models import failed: {e}")
        return False
    
    try:
        from backend.registry import SOURCES
        print("   ✅ Backend registry imported")
    except Exception as e:
        print(f"   ❌ Backend registry import failed: {e}")
        return False
    
    try:
        from backend.services.fetchers.random_art import fetch_artworks_from_sources
        print("   ✅ Random art fetcher imported")
    except Exception as e:
        print(f"   ❌ Random art fetcher import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from database.config import SessionLocal, init_db
        
        # Try to initialize database
        try:
            init_db()
            print("   ✅ Database initialization successful")
        except Exception as e:
            print(f"   ⚠️ Database initialization warning: {e}")
        
        # Try to create a session
        db = SessionLocal()
        print("   ✅ Database session created")
        
        # Test basic query
        try:
            count = db.query(Artwork).count()
            print(f"   ✅ Database query successful - {count} artworks found")
        except Exception as e:
            print(f"   ⚠️ Database query warning: {e}")
        
        db.close()
        print("   ✅ Database session closed")
        return True
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_api_sources():
    """Test available API sources"""
    print("\n🌐 Testing API sources...")
    
    try:
        from backend.registry import SOURCES
        
        available_sources = list(SOURCES.keys())
        print(f"   📊 Available sources: {len(available_sources)}")
        
        for source_name in available_sources:
            print(f"      - {source_name}")
        
        if not available_sources:
            print("   ❌ No sources available")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ API sources test failed: {e}")
        return False

def test_sample_fetch():
    """Test fetching a few sample artworks"""
    print("\n🎨 Testing sample artwork fetch...")
    
    try:
        from backend.services.fetchers.random_art import fetch_artworks_from_sources
        from backend.registry import SOURCES
        
        # Get first available source
        available_sources = list(SOURCES.keys())
        if not available_sources:
            print("   ❌ No sources available for testing")
            return False
        
        test_source = available_sources[0]
        print(f"   🔄 Testing with source: {test_source}")
        
        # Fetch 2 artworks as a test
        artworks = fetch_artworks_from_sources(
            seen_urls=set(),
            selected_sources=[test_source],
            max_per_source=2
        )
        
        if artworks:
            print(f"   ✅ Successfully fetched {len(artworks)} artworks")
            
            # Show sample data
            for i, artwork in enumerate(artworks[:2]):
                print(f"      Artwork {i+1}:")
                print(f"        Title: {artwork.get('title', 'N/A')}")
                print(f"        Artist: {artwork.get('artist', 'N/A')}")
                print(f"        Image URL: {artwork.get('image_url', 'N/A')[:50]}...")
                print(f"        Source: {artwork.get('source', 'N/A')}")
        else:
            print("   ⚠️ No artworks returned from test source")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample fetch test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Art Database Population System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection", test_database_connection),
        ("API Sources", test_api_sources),
        ("Sample Fetch", test_sample_fetch)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"   ✅ {test_name} PASSED")
        else:
            print(f"   ❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You can now run the population scripts.")
        print("\n💡 Next steps:")
        print("   1. Run: python scripts/quick_populate.py")
        print("   2. Or run: python scripts/populate_db_comprehensive.py")
    else:
        print("❌ Some tests failed. Please fix the issues before running population scripts.")
        print("\n🔧 Common fixes:")
        print("   - Check database configuration")
        print("   - Verify all dependencies are installed")
        print("   - Ensure you're running from the project root directory")

if __name__ == "__main__":
    main()
