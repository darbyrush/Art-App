import os
from typing import Optional
from pathlib import Path

class Config:
    """Configuration class for managing API keys and settings"""
    
    def __init__(self):
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists"""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
    
    @property
    def smithsonian_api_key(self) -> Optional[str]:
        """Get Smithsonian API key from environment variable"""
        return os.getenv("SMITHSONIAN_API_KEY")
    
    @property
    def cleveland_api_key(self) -> Optional[str]:
        """Get Cleveland API key from environment variable (if needed in future)"""
        return os.getenv("CLEVELAND_API_KEY")
    
    @property
    def met_api_key(self) -> Optional[str]:
        """Get MET API key from environment variable"""
        return os.getenv("MET_API_KEY")
    
    @property
    def harvard_api_key(self) -> Optional[str]:
        """Get Harvard API key from environment variable"""
        return os.getenv("HARVARD_API_KEY")
    
    def validate_api_keys(self) -> dict:
        """Validate that required API keys are available"""
        missing_keys = []
        available_keys = {}
        
        # Check Smithsonian (currently required)
        if self.smithsonian_api_key:
            available_keys["smithsonian"] = True
        else:
            missing_keys.append("SMITHSONIAN_API_KEY")
            available_keys["smithsonian"] = False
        
        # Check other APIs (optional for now)
        if self.met_api_key:
            available_keys["met"] = True
        else:
            available_keys["met"] = False
            
        if self.harvard_api_key:
            available_keys["harvard"] = True
        else:
            available_keys["harvard"] = False
            
        if self.cleveland_api_key:
            available_keys["cleveland"] = True
        else:
            available_keys["cleveland"] = False
        
        return {
            "missing_keys": missing_keys,
            "available_keys": available_keys
        }

# Global config instance
config = Config() 