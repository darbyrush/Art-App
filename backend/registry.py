from backend.services.fetchers.cleveland import fetch_from_cleveland
from backend.services.fetchers.met import fetch_from_met
from backend.services.fetchers.chicago import fetch_from_chicago  
from backend.services.fetchers.harvard import fetch_from_harvard
from backend.services.fetchers.smithsonian import fetch_from_smithsonian
from backend.services.fetchers.walters import fetch_from_walters
from backend.services.fetchers.national_gallery import fetch_from_national_gallery
from backend.config import config

# Validate API keys and only include available sources
def get_available_sources():
    """Get dictionary of available sources based on API key availability"""
    validation = config.validate_api_keys()
    available_keys = validation["available_keys"]
    
    sources = {}
    
    # Always include sources that don't require API keys
    sources["cleveland"] = fetch_from_cleveland
    sources["met"] = fetch_from_met
    sources["chicago"] = fetch_from_chicago
    sources["walters"] = fetch_from_walters  # No API key needed
    sources["national_gallery"] = fetch_from_national_gallery  # No API key needed
    
    # Include Smithsonian if API key is available
    if available_keys.get("smithsonian", False):
        sources["smithsonian"] = fetch_from_smithsonian
    else:
        print("Warning: Smithsonian API key not found. Smithsonian source will be disabled.")
    
    # Include Harvard if API key is available
    if available_keys.get("harvard", False):
        sources["harvard"] = fetch_from_harvard
    else:
        print("Info: Harvard API key not found. Harvard source will be disabled.")
    

    
    return sources

# Initialize available sources
SOURCES = get_available_sources()