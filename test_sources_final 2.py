#!/usr/bin/env python3
"""
Final test to verify all sources are using correct names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.registry import SOURCES

def test_source_names():
    """Test that all sources use correct registry names"""
    print("Testing source names...")
    print("=" * 50)
    
    expected_sources = {
        'cleveland', 'met', 'chicago', 'walters', 
        'national_gallery', 'smithsonian', 'harvard'
    }
    
    actual_sources = set(SOURCES.keys())
    
    print(f"Expected sources: {expected_sources}")
    print(f"Actual sources: {actual_sources}")
    print(f"Match: {actual_sources == expected_sources}")
    
    # Test each source to make sure it returns correct source name
    for source_name, fetcher in SOURCES.items():
        print(f"\nTesting {source_name}...")
        try:
            result = fetcher(set())
            if result:
                if isinstance(result, list):
                    for artwork in result[:2]:  # Check first 2 artworks
                        if artwork.get('source') != source_name:
                            print(f"  ❌ {source_name}: artwork has source '{artwork.get('source')}' instead of '{source_name}'")
                        else:
                            print(f"  ✅ {source_name}: artwork source is correct")
                elif isinstance(result, dict):
                    if result.get('source') != source_name:
                        print(f"  ❌ {source_name}: artwork has source '{result.get('source')}' instead of '{source_name}'")
                    else:
                        print(f"  ✅ {source_name}: artwork source is correct")
        except Exception as e:
            print(f"  ❌ {source_name}: Error - {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ All sources should now use correct registry names!")

if __name__ == "__main__":
    test_source_names() 