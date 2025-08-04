#!/usr/bin/env python3
"""
Art Explorer - Application Configuration
Centralized configuration for the Streamlit application
"""

import os
from typing import List, Dict, Any

class AppConfig:
    """Application configuration class"""
    
    # App metadata
    APP_NAME = "Art Explorer"
    APP_VERSION = "1.0.0"
    APP_ICON = "🎨"
    
    # Page configuration
    PAGE_CONFIG = {
        "page_title": APP_NAME,
        "page_icon": APP_ICON,
        "layout": "wide",
        "initial_sidebar_state": "collapsed"
    }
    
    # API configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = 30
    
    # Available museum sources (updated based on testing)
    AVAILABLE_SOURCES = [
        'all',
        'Cleveland Museum of Art',
        'Metropolitan Museum of Art', 
        'Art Institute of Chicago',
        'Walters Art Museum', 
        'National Gallery of Art',
        'Smithsonian American Art Museum', 
        'Harvard Art Museums'
    ]
    
    # Default sources
    DEFAULT_SOURCES = ['all']
    
    # Session state keys
    SESSION_KEYS = {
        'artwork_history': [],
        'current_index': -1
    }
    
    # UI Configuration
    UI_CONFIG = {
        'instagram_container_max_width': '600px',
        'artwork_image_height': '600px',
        'double_tap_threshold': 500,  # milliseconds
        'heart_overlay_duration': 1000  # milliseconds
    }
    
    # Color scheme
    COLORS = {
        'primary': '#667eea',
        'secondary': '#764ba2',
        'accent': '#e74c3c',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'text_muted': '#95a5a6',
        'background': '#f8f9fa',
        'white': '#ffffff'
    }
    
    # CSS Styles
    @staticmethod
    def get_css_styles() -> str:
        """Get the main CSS styles for the application"""
        return """
        <style>
            .main-header {
                text-align: center;
                color: #2c3e50;
                font-size: 2.5rem;
                margin-bottom: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .instagram-container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                overflow: hidden;
                position: relative;
            }
            
            .artwork-header {
                padding: 1rem;
                border-bottom: 1px solid #eee;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .artwork-source {
                font-weight: bold;
                color: #2c3e50;
                font-size: 1.1rem;
            }
            
            .artwork-image-container {
                position: relative;
                width: 100%;
                height: 600px;
                overflow: hidden;
                cursor: pointer;
            }
            
            .artwork-image {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }
            
            .double-tap-overlay {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 4rem;
                color: #e74c3c;
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
                z-index: 10;
            }
            
            .double-tap-overlay.show {
                opacity: 1;
            }
            
            .artwork-info {
                padding: 1rem;
                border-top: 1px solid #eee;
            }
            
            .artwork-title {
                font-size: 1.3rem;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 0.5rem;
            }
            
            .artwork-artist {
                font-size: 1rem;
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 1rem;
            }
            
            .artwork-metadata {
                font-size: 0.9rem;
                color: #95a5a6;
                line-height: 1.4;
            }
            
            .navigation-buttons {
                display: flex;
                justify-content: space-between;
                padding: 1rem;
                background: white;
                border-top: 1px solid #eee;
            }
            
            .nav-button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                font-size: 1rem;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
            }
            
            .nav-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .like-button {
                background: linear-gradient(45deg, #e74c3c, #c0392b);
                color: white;
                border: none;
                padding: 0.8rem 1.5rem;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                font-size: 1rem;
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                transition: all 0.3s ease;
            }
            
            .like-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
            }
            
            .stats-mini {
                display: flex;
                justify-content: space-around;
                padding: 0.5rem;
                background: #f8f9fa;
                border-radius: 10px;
                margin: 1rem 0;
                font-size: 0.9rem;
            }
            
            .stat-item {
                text-align: center;
            }
            
            .stat-value {
                font-weight: bold;
                color: #667eea;
            }
            
            .stat-label {
                color: #7f8c8d;
                font-size: 0.8rem;
            }
            
            .empty-state {
                text-align: center;
                padding: 3rem;
                color: #7f8c8d;
            }
            
            .sidebar-section {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
        </style>
        """
    
    # JavaScript for double-tap functionality
    @staticmethod
    def get_double_tap_js() -> str:
        """Get JavaScript for double-tap functionality"""
        return """
        <script>
        let lastTap = 0;
        let tapCount = 0;
        
        function handleDoubleTap() {
            const now = Date.now();
            const timeDiff = now - lastTap;
            
            if (timeDiff < 500 && timeDiff > 0) {
                // Double tap detected
                const overlay = document.getElementById('heart-overlay');
                overlay.classList.add('show');
                
                // Send like to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: 'like'
                }, '*');
                
                setTimeout(() => {
                    overlay.classList.remove('show');
                }, 1000);
            }
            
            lastTap = now;
        }
        </script>
        """

# Global configuration instance
config = AppConfig() 