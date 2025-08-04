import requests
import streamlit as st
from typing import Optional, Dict, List
import json

class APIClient:
    """Client for communicating with the Art Explorer API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token if available"""
        headers = {"Content-Type": "application/json"}
        token = st.session_state.get('access_token')
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Dict:
        """Register a new user"""
        data = {
            "username": username,
            "password": password
        }
        if email:
            data["email"] = email
            
        response = self.session.post(
            f"{self.base_url}/register",
            json=data,
            headers=self._get_headers()
        )
        return response.json() if response.status_code == 200 else None
    
    def login_user(self, username: str, password: str) -> Optional[str]:
        """Login user and return access token"""
        data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        return None
    
    def get_random_artwork(self, sources: List[str] = None) -> Optional[Dict]:
        """Get a random artwork from specified sources"""
        params = {}
        if sources and "all" not in sources:
            params["sources"] = ",".join(sources)
        
        headers = self._get_headers()
        
        # Debug: Check if we have authentication token
        if not headers.get("Authorization"):
            print("Warning: No authentication token found")
            return None
        
        response = self.session.get(
            f"{self.base_url}/artworks/random",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Error: Unauthorized - Authentication required")
            return None
        elif response.status_code == 404:
            print("Error: Not found - Endpoint not available")
            return None
        else:
            print(f"Error: HTTP {response.status_code} - {response.text}")
            return None
    
    def like_artwork(self, artwork_id: str, liked: bool = True) -> bool:
        """Like or dislike an artwork"""
        data = {"liked": liked}
        
        response = self.session.post(
            f"{self.base_url}/artworks/{artwork_id}/like",
            json=data,
            headers=self._get_headers()
        )
        
        return response.status_code == 200
    
    def rate_artwork(self, artwork_id: str, rating: int) -> bool:
        """Rate an artwork (1-5 stars)"""
        data = {"rating": rating}
        
        response = self.session.post(
            f"{self.base_url}/artworks/{artwork_id}/rate",
            json=data,
            headers=self._get_headers()
        )
        
        return response.status_code == 200
    
    def add_note(self, artwork_id: str, note: str) -> bool:
        """Add a note to an artwork"""
        data = {"note": note}
        
        response = self.session.post(
            f"{self.base_url}/artworks/{artwork_id}/note",
            json=data,
            headers=self._get_headers()
        )
        
        return response.status_code == 200
    
    def get_user_likes(self) -> List[Dict]:
        """Get all artworks liked by current user"""
        response = self.session.get(
            f"{self.base_url}/users/me/likes",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        response = self.session.get(
            f"{self.base_url}/users/me/stats",
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return {
            "total_artworks": 0,
            "liked_artworks": 0,
            "unique_museums": 0,
            "avg_rating": 0
        }
    
    def search_artworks(self, source: Optional[str] = None, 
                       artist: Optional[str] = None, 
                       date_range: Optional[str] = None) -> List[Dict]:
        """Search artworks with filters"""
        params = {}
        if source:
            params["source"] = source
        if artist:
            params["artist"] = artist
        if date_range:
            params["date_range"] = date_range
        
        response = self.session.get(
            f"{self.base_url}/artworks/search",
            params=params,
            headers=self._get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

# Global API client instance
api_client = APIClient() 