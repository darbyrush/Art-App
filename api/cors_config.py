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

def get_cors_middleware():
    # Get CORS origins from environment variable or use defaults
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    
    # Default origins for development and production
    default_origins = [
        "https://myassemblage.art",
        "https://www.myassemblage.art", 
        "https://api.myassemblage.art",
        "https://art-app-frontend.vercel.app",  # Vercel frontend
        "https://*.vercel.app",  # Any Vercel subdomain
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]
    
    # Combine environment origins with defaults, removing empty strings
    all_origins = [origin.strip() for origin in cors_origins if origin.strip()] + default_origins
    
    return CORSMiddleware(
        allow_origins=all_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 