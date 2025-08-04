from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

def is_vercel_domain(origin: str) -> bool:
    """Check if origin is a Vercel domain"""
    return origin.startswith("https://") and ".vercel.app" in origin

class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        origin = request.headers.get("origin")
        if origin:
            # Allow all Vercel domains automatically
            if is_vercel_domain(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "*"
                response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

def get_cors_middleware():
    """Get CORS middleware configuration"""
    cors_origins = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "https://art-app-backend.railway.app",
        "https://art-app.railway.internal"
    ]
    
    # Add production origins from environment variable
    import os
    if os.getenv("CORS_ORIGINS"):
        cors_origins.extend(os.getenv("CORS_ORIGINS").split(","))
    
    return CORSMiddleware(
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 