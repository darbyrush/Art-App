from backend.services.fetchers.cleveland import fetch_from_cleveland
from backend.services.fetchers.met import fetch_from_met
from backend.services.fetchers.chicago import fetch_from_chicago  
# from backend.services.fetchers.rijks import fetch_from_rijks
from backend.services.fetchers.harvard import fetch_from_harvard
from backend.services.fetchers.smithsonian import fetch_from_smithsonian
from backend.config import config

# Validate API keys and only include available sources
def get_available_sources():
    """Get dictionary of available sources based on API key availability"""
    validation = config.validate_api_keys()
    available_keys = validation["available_keys"]
    
    sources = {}
    
    # Always include Cleveland (no API key required)
    sources["cleveland"] = fetch_from_cleveland
    
    # Always include MET (no API key required)
    sources["met"] = fetch_from_met
    
    # Always include Chicago (no API key required)
    sources["chicago"] = fetch_from_chicago
    
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