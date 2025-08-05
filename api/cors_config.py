from fastapi.middleware.cors import CORSMiddleware

def get_cors_origins():
    """Get CORS origins configuration"""
    cors_origins = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "https://art-app-backend.railway.app",
        "https://art-app.railway.internal",
        "https://art-app.railway.app",
        # Add wildcard for any Railway domain
        "https://*.railway.app",
        # Add all known Vercel domains
        "https://art-app-rosy.vercel.app",
        "https://art-oxd1cyyg6-darbyrushs-projects.vercel.app",
        "https://art-our6lxwlw-darbyrushs-projects.vercel.app",
        "https://art-cz49xzb9h-darbyrushs-projects.vercel.app",
        "https://art-bey5mvj3s-darbyrushs-projects.vercel.app",
        "https://art-app.vercel.app",
        "https://art-explorer.vercel.app",
        "https://art-gallery.vercel.app",
        # Add wildcard for any Vercel domain
        "https://*.vercel.app"
    ]
    
    # Add production origins from environment variable
    import os
    if os.getenv("CORS_ORIGINS"):
        cors_origins.extend(os.getenv("CORS_ORIGINS").split(","))
    
    return cors_origins 