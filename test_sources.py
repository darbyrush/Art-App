#!/usr/bin/env python3
"""
Test script to check which art sources are working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.registry import SOURCES
from backend.config import config

def test_sources():
    """Test all available sources"""
    print("Testing available art sources...")
    print("=" * 50)
    
    # Check API key validation
    validation = config.validate_api_keys()
    print(f"API Key Status:")
    for key, available in validation["available_keys"].items():
        status = "✅" if available else "❌"
        print(f"  {key}: {status}")
    
    print(f"\nAvailable Sources ({len(SOURCES)}):")
    print("=" * 30)
    
    working_sources = []
    for source_name, fetcher in SOURCES.items():
        print(f"\nTesting {source_name}...")
        try:
            # Test the fetcher
            result = fetcher(set())
            
            if result:
                if isinstance(result, list):
                    count = len(result)
                    has_images = sum(1 for art in result if art.get('image_url'))
                    print(f"  ✅ {source_name}: {count} artworks, {has_images} with images")
                    working_sources.append(source_name)
                elif isinstance(result, dict):
                    has_image = bool(result.get('image_url'))
                    print(f"  ✅ {source_name}: 1 artwork, {'with' if has_image else 'no'} image")
                    working_sources.append(source_name)
                else:
                    print(f"  ❌ {source_name}: Unexpected result type")
            else:
                print(f"  ❌ {source_name}: No results")
                
        except Exception as e:
            print(f"  ❌ {source_name}: Error - {e}")
    
    print(f"\n" + "=" * 50)
    print(f"Working sources: {working_sources}")
    print(f"Total working: {len(working_sources)}/{len(SOURCES)}")
    
    return working_sources

if __name__ == "__main__":
    test_sources() 