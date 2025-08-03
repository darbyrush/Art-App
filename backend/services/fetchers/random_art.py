import random
from typing import List, Set, Dict, Optional
from backend.metadata import MetadataProcessor

def fetch_random_artwork(seen_urls: set[str], sources=None, selected_sources=None):
    """
    Fetch random artwork from selected sources.
    
    Args:
        seen_urls: Set of already seen image URLs
        sources: Dictionary of available fetchers (defaults to SOURCES)
        selected_sources: List of source names to use (if None, uses all)
    """
    if sources is None:
        # Import here to avoid circular import
        from backend.registry import SOURCES
        sources = SOURCES
    
    # Filter sources if specific ones are selected
    if selected_sources:
        available_sources = {k: v for k, v in sources.items() if k in selected_sources}
    else:
        available_sources = sources
    
    if not available_sources:
        return None
    
    all_artworks = []
    
    # Try each source until we find artworks
    source_names = list(available_sources.keys())
    random.shuffle(source_names)  # Randomize source order
    
    for source_name in source_names:
        fetcher = available_sources[source_name]
        try:
            result = fetcher(seen_urls)
            if isinstance(result, list):
                # Enrich metadata for each artwork
                enriched_results = []
                for artwork in result:
                    enriched_artwork = MetadataProcessor.enrich_metadata(artwork)
                    enriched_artwork['search_tags'] = MetadataProcessor.get_search_tags(enriched_artwork)
                    enriched_results.append(enriched_artwork)
                all_artworks.extend(enriched_results)
            elif isinstance(result, dict):
                # Enrich single artwork
                enriched_artwork = MetadataProcessor.enrich_metadata(result)
                enriched_artwork['search_tags'] = MetadataProcessor.get_search_tags(enriched_artwork)
                all_artworks.append(enriched_artwork)
            
            # If we have enough artworks, stop fetching
            if len(all_artworks) >= 20:
                break
                
        except Exception as e:
            print(f"Error in {source_name} fetcher: {e}")
            continue
    
    # Filter out seen artworks and invalid ones
    unseen_artworks = [
        art for art in all_artworks 
        if art.get('image_url') and 
        art['image_url'] not in seen_urls and
        not art['image_url'].lower().endswith('.gif')
    ]
    
    return random.choice(unseen_artworks) if unseen_artworks else None

def fetch_artworks_from_sources(seen_urls: set[str], selected_sources: List[str], max_per_source: int = 5):
    """
    Fetch artworks from multiple selected sources.
    
    Args:
        seen_urls: Set of already seen image URLs
        selected_sources: List of source names to fetch from
        max_per_source: Maximum artworks to fetch per source
    
    Returns:
        List of artworks from all selected sources
    """
    if not selected_sources:
        return []
    
    # Import here to avoid circular import
    from backend.registry import SOURCES
    
    all_artworks = []
    
    for source_name in selected_sources:
        if source_name not in SOURCES:
            continue
            
        fetcher = SOURCES[source_name]
        try:
            result = fetcher(seen_urls)
            if isinstance(result, list):
                # Limit artworks per source and enrich metadata
                source_artworks = result[:max_per_source]
                enriched_artworks = []
                for artwork in source_artworks:
                    enriched_artwork = MetadataProcessor.enrich_metadata(artwork)
                    enriched_artwork['search_tags'] = MetadataProcessor.get_search_tags(enriched_artwork)
                    enriched_artworks.append(enriched_artwork)
                all_artworks.extend(enriched_artworks)
            elif isinstance(result, dict):
                # Enrich single artwork
                enriched_artwork = MetadataProcessor.enrich_metadata(result)
                enriched_artwork['search_tags'] = MetadataProcessor.get_search_tags(enriched_artwork)
                all_artworks.append(enriched_artwork)
                
        except Exception as e:
            print(f"Error in {source_name} fetcher: {e}")
            continue
    
    # Filter out seen artworks and invalid ones
    unseen_artworks = [
        art for art in all_artworks 
        if art.get('image_url') and 
        art['image_url'] not in seen_urls and
        not art['image_url'].lower().endswith('.gif')
    ]
    
    return unseen_artworks