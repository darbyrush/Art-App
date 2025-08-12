from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import os
import time
import logging
from typing import List, Optional

# Import schemas and models - use the correct import paths for production
try:
    # Try production imports first (when running in Docker container)
    from api.database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
    from api.database.config import get_db, init_db, test_connection
    from api.schemas import (
        UserCreate, UserResponse, UserUpdate, UserLikeCreate, UserRatingCreate, 
        UserNoteCreate, BoardCreate, BoardResponse, BoardUpdate, BoardArtworkCreate,
        ArtworkResponse, Token
    )
    from api.services import UserService
    from api.auth import get_current_user, create_access_token, get_password_hash
    logging.info("✅ Using production import paths")
except ImportError:
    try:
        # Fallback to development imports (when running locally)
        from database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
        from database.config import get_db, init_db, test_connection
        from schemas import (
            UserCreate, UserResponse, UserUpdate, UserLikeCreate, UserRatingCreate, 
            UserNoteCreate, BoardCreate, BoardResponse, BoardUpdate, BoardArtworkCreate,
            ArtworkResponse, Token
        )
        from services import UserService
        from auth import get_current_user, create_access_token, get_password_hash
        logging.info("✅ Using development import paths")
    except ImportError as e:
        logging.error(f"❌ All import attempts failed: {e}")
        raise

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Art Explorer API",
    description="Simple Art Explorer API - Clean and Working",
    version="1.0.0"
)

# Add CORS middleware with robust configuration
try:
    # Try to use the external CORS config if available
    from api.cors_config import get_cors_middleware
    app.add_middleware(get_cors_middleware())
    logger.info("✅ Using external CORS configuration")
except ImportError:
    try:
        # Fallback to local CORS config
        from cors_config import get_cors_middleware
        app.add_middleware(get_cors_middleware())
        logger.info("✅ Using local CORS configuration")
    except ImportError:
        # Final fallback: use basic CORS configuration
        logger.warning("⚠️ External CORS config not available, using basic CORS")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://myassemblage.art",
                "https://www.myassemblage.art",
                "http://localhost:3000",
                "http://localhost:5173"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Simple startup event
@app.on_event("startup")
async def startup_event():
    """Simple startup - just initialize database"""
    logger.info("🚀 Starting Art Explorer API...")
    
    try:
        # Ensure uploads directory exists
        uploads_dir = "uploads/profile_pictures"
        os.makedirs(uploads_dir, exist_ok=True)
        logger.info(f"✅ Uploads directory ensured: {uploads_dir}")
        
        # Initialize database - but don't crash if it fails
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization failed: {e}")
            logger.info("🔄 Continuing without database initialization")
        
        # Test connection - but don't crash if it fails
        try:
            if test_connection():
                logger.info("✅ Database connection test passed")
            else:
                logger.warning("⚠️ Database connection test failed")
        except Exception as e:
            logger.warning(f"⚠️ Database connection test failed: {e}")
            logger.info("🔄 Continuing without database connection")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        logger.info("🔄 Continuing anyway - don't crash the app")
    
    logger.info("🎉 Art Explorer API startup completed!")

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root endpoint
@app.get("/")
def root_endpoint():
    """Root endpoint - API information"""
    return {
        "message": "Art Explorer API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check
@app.get("/health")
def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Auth endpoints
@app.post("/auth/login")
def auth_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Simple login endpoint"""
    try:
        user_service = UserService()
        user = user_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    except ImportError as e:
        logger.error(f"Import error in login: {e}")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/register")
def auth_register(user: UserCreate, db: Session = Depends(get_db)):
    """Simple register endpoint"""
    try:
        user_service = UserService()
        
        # Check if user exists
        db_user = user_service.get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Create user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create token
        access_token = create_access_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        }
    except ImportError as e:
        logger.error(f"Import error in register: {e}")
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User endpoints
@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    return current_user

# Artwork endpoints
@app.get("/artworks", response_model=List[ArtworkResponse])
def get_artworks(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get artworks with pagination"""
    try:
        offset = (page - 1) * limit
        artworks = db.query(Artwork).offset(offset).limit(limit).all()
        return artworks
    except Exception as e:
        logger.error(f"Error getting artworks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Board endpoints
@app.get("/boards", response_model=List[BoardResponse])
def get_user_boards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's boards"""
    try:
        boards = db.query(Board).filter(Board.user_id == current_user.id).all()
        return boards
    except Exception as e:
        logger.error(f"Error getting boards: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return Response(
        content="Internal server error",
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Railway sets this) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
