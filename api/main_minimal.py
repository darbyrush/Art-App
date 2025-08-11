from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Art Explorer API",
    description="Ultra-Minimal Art Explorer API - Just the Basics",
    version="1.0.0"
)

# Simple CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple startup event
@app.on_event("startup")
async def startup_event():
    """Simple startup - just log success"""
    logger.info("🚀 Starting Art Explorer API...")
    logger.info("🎉 Art Explorer API startup completed!")

# Root endpoint
@app.get("/")
def root_endpoint():
    """Root endpoint - API information"""
    return {
        "message": "Art Explorer API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": "2024-01-XX"
    }

# Health check
@app.get("/health")
def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "message": "API is running"
    }

# Test endpoint
@app.get("/test")
def test_endpoint():
    """Test endpoint"""
    return {
        "message": "Test endpoint working",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
