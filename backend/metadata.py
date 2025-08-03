import re
from typing import Dict, List, Optional
from datetime import datetime

class MetadataProcessor:
    """Process and standardize artwork metadata from different sources"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text or text == "Unknown":
            return "Unknown"
        return text.strip()
    
    @staticmethod
    def extract_year(date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str or date_str == "Unknown":
            return None
        
        # Common patterns
        patterns = [
            r'(\d{4})',  # Just year
            r'c\.\s*(\d{4})',  # circa year
            r'(\d{4})-\d{4}',  # year range
            r'(\d{4})s',  # decade
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def categorize_period(year: Optional[int]) -> str:
        """Categorize artwork by time period"""
        if not year:
            return "Unknown"
        
        if year < 1400:
            return "Medieval"
        elif year < 1500:
            return "Early Renaissance"
        elif year < 1600:
            return "Renaissance"
        elif year < 1700:
            return "Baroque"
        elif year < 1800:
            return "Rococo/Neoclassical"
        elif year < 1900:
            return "19th Century"
        elif year < 1950:
            return "Early Modern"
        elif year < 2000:
            return "Modern"
        else:
            return "Contemporary"
    
    @staticmethod
    def standardize_artist(artist: str) -> str:
        """Standardize artist name"""
        if not artist or artist == "Unknown":
            return "Unknown"
        
        # Remove common prefixes/suffixes
        artist = re.sub(r'^(Unknown|Anonymous|Artist)\s*', '', artist)
        artist = re.sub(r'\s*\([^)]*\)$', '', artist)  # Remove parenthetical info
        
        return artist.strip() or "Unknown"
    
    @staticmethod
    def extract_medium(description: str) -> str:
        """Extract medium from description"""
        if not description:
            return "Unknown"
        
        mediums = {
            'oil': 'Oil on Canvas',
            'acrylic': 'Acrylic',
            'watercolor': 'Watercolor',
            'gouache': 'Gouache',
            'tempera': 'Tempera',
            'fresco': 'Fresco',
            'pastel': 'Pastel',
            'charcoal': 'Charcoal',
            'pencil': 'Pencil',
            'ink': 'Ink',
            'print': 'Print',
            'etching': 'Etching',
            'lithograph': 'Lithograph',
            'woodcut': 'Woodcut',
            'sculpture': 'Sculpture',
            'marble': 'Marble',
            'bronze': 'Bronze',
            'ceramic': 'Ceramic',
            'photograph': 'Photograph',
        }
        
        description_lower = description.lower()
        for key, value in mediums.items():
            if key in description_lower:
                return value
        
        return "Unknown"
    
    @staticmethod
    def enrich_metadata(artwork: Dict) -> Dict:
        """Enrich artwork metadata with additional information"""
        enriched = artwork.copy()
        
        # Clean basic fields
        enriched['title'] = MetadataProcessor.clean_text(artwork.get('title', ''))
        enriched['artist'] = MetadataProcessor.standardize_artist(artwork.get('artist', ''))
        enriched['date'] = MetadataProcessor.clean_text(artwork.get('date', ''))
        enriched['origin'] = MetadataProcessor.clean_text(artwork.get('origin', ''))
        enriched['department'] = MetadataProcessor.clean_text(artwork.get('department', ''))
        
        # Extract year and categorize period
        year = MetadataProcessor.extract_year(enriched['date'])
        enriched['year'] = year
        enriched['period'] = MetadataProcessor.categorize_period(year)
        
        # Extract medium from description or department
        description = artwork.get('description', '') or artwork.get('department', '')
        enriched['medium'] = MetadataProcessor.extract_medium(description)
        
        # Add source-specific metadata
        source = artwork.get('source', 'Unknown')
        enriched['source_category'] = MetadataProcessor.categorize_source(source)
        
        return enriched
    
    @staticmethod
    def categorize_source(source: str) -> str:
        """Categorize museum by type"""
        source_lower = source.lower()
        
        if 'national' in source_lower or 'smithsonian' in source_lower:
            return 'National Museum'
        elif 'metropolitan' in source_lower or 'met' in source_lower:
            return 'Major Art Museum'
        elif 'harvard' in source_lower or 'university' in source_lower:
            return 'University Museum'
        elif 'cleveland' in source_lower or 'chicago' in source_lower:
            return 'City Museum'
        else:
            return 'Art Museum'
    
    @staticmethod
    def get_search_tags(artwork: Dict) -> List[str]:
        """Generate search tags for artwork"""
        tags = []
        
        # Add period
        if artwork.get('period') and artwork['period'] != 'Unknown':
            tags.append(artwork['period'])
        
        # Add medium
        if artwork.get('medium') and artwork['medium'] != 'Unknown':
            tags.append(artwork['medium'])
        
        # Add source category
        if artwork.get('source_category'):
            tags.append(artwork['source_category'])
        
        # Add origin/culture
        if artwork.get('origin') and artwork['origin'] != 'Unknown':
            tags.append(artwork['origin'])
        
        return list(set(tags))  # Remove duplicates 