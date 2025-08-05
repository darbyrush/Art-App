from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        origin = request.headers.get("origin")
        if origin:
            # Allow ALL origins dynamically
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

import os

def get_cors_origins():
    """Get CORS origins configuration"""
    # Check for environment variable first
    cors_origins_env = os.getenv("CORS_ORIGINS")
    if cors_origins_env:
        # Split by comma if multiple origins are provided
        return [origin.strip() for origin in cors_origins_env.split(",")]
    
    # Default origins
    return [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "https://art-6y598lbos-darbyrushs-projects.vercel.app",
        "https://art-app-production.up.railway.app",
        "https://*.vercel.app",
        "https://*.railway.app",
        "*"  # Fallback for development
    ] 