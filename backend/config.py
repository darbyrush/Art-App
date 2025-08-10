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
    def environment(self) -> str:
        """Get current environment"""
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    @property
    def secret_key(self) -> str:
        """Get secret key for JWT tokens"""
        key = os.getenv("SECRET_KEY")
        if not key and self.is_production:
            raise ValueError("SECRET_KEY must be set in production")
        return key or "dev-secret-key-change-in-production"
    
    @property
    def cors_origins(self) -> list:
        """Get CORS origins"""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        return [origin.strip() for origin in origins.split(",")]
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return os.getenv("DATABASE_URL", "sqlite:///./art_explorer.db")
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        return os.getenv("REDIS_URL", "redis://localhost:6379")
    
    @property
    def max_upload_size(self) -> int:
        """Get maximum upload size in bytes (default: 10MB)"""
        return int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    
    @property
    def rate_limit_requests(self) -> int:
        """Get rate limit requests per minute"""
        return int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    
    @property
    def rate_limit_window(self) -> int:
        """Get rate limit window in seconds"""
        return int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    @property
    def log_level(self) -> str:
        """Get log level"""
        return os.getenv("LOG_LEVEL", "INFO" if self.is_production else "DEBUG")
    
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
    
    @property
    def europeana_api_key(self) -> Optional[str]:
        """Get Europeana API key from environment variable"""
        return os.getenv("EUROPEANA_API_KEY")
    
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
        
        if self.europeana_api_key:
            available_keys["europeana"] = True
        else:
            available_keys["europeana"] = False
        
        return {
            "missing_keys": missing_keys,
            "available_keys": available_keys
        }
    
    def validate_production_config(self) -> dict:
        """Validate production configuration"""
        errors = []
        warnings = []
        
        if self.is_production:
            if not self.secret_key or self.secret_key == "dev-secret-key-change-in-production":
                errors.append("SECRET_KEY must be set in production")
            
            if not self.database_url.startswith("postgresql"):
                warnings.append("Consider using PostgreSQL in production")
            
            if not self.redis_url.startswith("redis://"):
                warnings.append("Consider using Redis in production for caching")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0
        }

# Global config instance
config = Config() 