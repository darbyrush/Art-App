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

# Import schemas and models - use correct paths for container
from database.models import User, UserLike, UserRating, UserNote, Board, BoardArtwork, Artwork
from database.config import get_db, init_db, test_connection
from schemas import (
    UserCreate, UserResponse, UserUpdate, UserLikeCreate, UserRatingCreate, 
    UserNoteCreate, BoardCreate, BoardResponse, BoardUpdate, BoardArtworkCreate,
    ArtworkResponse, Token
)
from services import UserService
from auth import get_current_user, create_access_token, get_password_hash

logging.info("✅ Using production import paths")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Art Explorer API",
    description="Simple Art Explorer API - Clean and Working",
    version="1.0.0"
)

# Add CORS middleware using Railway environment variables directly
# Get CORS origins from Railway environment variables
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

# Default origins for development and production
default_origins = [
    "https://myassemblage.art",
    "https://www.myassemblage.art",
    "http://localhost:3000",
    "http://localhost:5173"
]

# Vercel-Railway native connection origins
vercel_origins = [
    "https://myassemblage.art.vercel.app",  # Vercel domain
    "https://*.vercel.app",                 # Any Vercel subdomain
    "https://*.railway.app",                # Any Railway subdomain
]

# Combine all origins
all_origins = cors_origins + default_origins + vercel_origins

# Remove duplicates while preserving order
seen = set()
unique_origins = []
for origin in all_origins:
    if origin not in seen:
        seen.add(origin)
        unique_origins.append(origin)

logger.info(f"✅ CORS origins configured: {unique_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=unique_origins,
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

# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Art Explorer API",
        "status": "running",
        "version": "1.0.0",
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
        
        # Add artwork count to each board
        for board in boards:
            board.artwork_count = db.query(BoardArtwork).filter(BoardArtwork.board_id == board.id).count()
        
        return boards
    except Exception as e:
        logger.error(f"Error getting boards: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/boards", response_model=BoardResponse)
def create_board(board: BoardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new board"""
    try:
        db_board = Board(
            name=board.name,
            description=board.description,
            is_public=board.is_public,
            user_id=current_user.id
        )
        db.add(db_board)
        db.commit()
        db.refresh(db_board)
        
        # Add artwork count (will be 0 for new boards)
        db_board.artwork_count = 0
        
        return db_board
    except Exception as e:
        logger.error(f"Error creating board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/boards/{board_id}", response_model=BoardResponse)
def get_board(board_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Add artwork count
        board.artwork_count = db.query(BoardArtwork).filter(BoardArtwork.board_id == board.id).count()
        
        return board
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/boards/{board_id}", response_model=BoardResponse)
def update_board(board_id: int, board_update: BoardUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        if board_update.name is not None:
            board.name = board_update.name
        if board_update.description is not None:
            board.description = board_update.description
        if board_update.is_public is not None:
            board.is_public = board_update.is_public
        
        db.commit()
        db.refresh(board)
        
        # Add artwork count
        board.artwork_count = db.query(BoardArtwork).filter(BoardArtwork.board_id == board.id).count()
        
        return board
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/boards/{board_id}")
def delete_board(board_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        db.delete(board)
        db.commit()
        return {"message": "Board deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/boards/{board_id}/artworks", response_model=List[ArtworkResponse])
def get_board_artworks(board_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get artworks in a board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Get artworks through the BoardArtwork relationship
        board_artworks = db.query(BoardArtwork).filter(BoardArtwork.board_id == board_id).all()
        artwork_ids = [ba.artwork_id for ba in board_artworks]
        
        if not artwork_ids:
            return []
        
        artworks = db.query(Artwork).filter(Artwork.id.in_(artwork_ids)).all()
        return artworks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting board artworks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/boards/{board_id}/artworks")
def add_artwork_to_board(board_id: int, board_artwork: BoardArtworkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add an artwork to a board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Check if artwork already exists in board
        existing = db.query(BoardArtwork).filter(
            BoardArtwork.board_id == board_id,
            BoardArtwork.artwork_id == board_artwork.artwork_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Artwork already in board")
        
        # Check if artwork exists
        artwork = db.query(Artwork).filter(Artwork.id == board_artwork.artwork_id).first()
        if not artwork:
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        db_board_artwork = BoardArtwork(
            board_id=board_id,
            artwork_id=board_artwork.artwork_id
        )
        db.add(db_board_artwork)
        db.commit()
        
        return {"message": "Artwork added to board successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding artwork to board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/boards/{board_id}/artworks/{artwork_id}")
def remove_artwork_from_board(board_id: int, artwork_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove an artwork from a board"""
    try:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == current_user.id).first()
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        board_artwork = db.query(BoardArtwork).filter(
            BoardArtwork.board_id == board_id,
            BoardArtwork.artwork_id == artwork_id
        ).first()
        
        if not board_artwork:
            raise HTTPException(status_code=404, detail="Artwork not in board")
        
        db.delete(board_artwork)
        db.commit()
        
        return {"message": "Artwork removed from board successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing artwork from board: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Liked artworks endpoints
@app.get("/artworks/liked", response_model=List[ArtworkResponse])
def get_liked_artworks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    sources: Optional[str] = None,
    artist: Optional[str] = None,
    date_from: Optional[int] = None,
    date_to: Optional[int] = None,
    sort_by: str = "date_liked"
):
    """Get user's liked artworks with filters"""
    try:
        query = db.query(Artwork).join(UserLike).filter(UserLike.user_id == current_user.id)
        
        # Apply filters
        if sources and sources != "all":
            source_list = sources.split(",")
            query = query.filter(Artwork.source.in_(source_list))
        
        if artist:
            query = query.filter(Artwork.artist.ilike(f"%{artist}%"))
        
        if date_from:
            query = query.filter(Artwork.date >= date_from)
        
        if date_to:
            query = query.filter(Artwork.date <= date_to)
        
        # Apply sorting
        if sort_by == "title":
            query = query.order_by(Artwork.title)
        elif sort_by == "artist":
            query = query.order_by(Artwork.artist)
        elif sort_by == "date":
            query = query.order_by(Artwork.date)
        elif sort_by == "source":
            query = query.order_by(Artwork.source)
        else:  # date_liked (default)
            query = query.order_by(UserLike.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        artworks = query.offset(offset).limit(limit).all()
        
        return artworks
    except Exception as e:
        logger.error(f"Error getting liked artworks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/artworks/liked/filters")
def get_liked_artworks_filter_options(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get filter options for liked artworks"""
    try:
        # Get unique sources
        sources = db.query(Artwork.source).join(UserLike).filter(
            UserLike.user_id == current_user.id
        ).distinct().all()
        source_list = [source[0] for source in sources if source[0]]
        
        # Get unique artists
        artists = db.query(Artwork.artist).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            Artwork.artist.isnot(None)
        ).distinct().all()
        artist_list = [artist[0] for artist in artists if artist[0]]
        
        # Get date range
        date_range = db.query(
            db.func.min(Artwork.date),
            db.func.max(Artwork.date)
        ).join(UserLike).filter(UserLike.user_id == current_user.id).first()
        
        return {
            "sources": source_list,
            "artists": artist_list,
            "dateRange": {
                "min": date_range[0] if date_range[0] else None,
                "max": date_range[1] if date_range[1] else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Artwork like/unlike endpoints
@app.post("/artworks/{artwork_id}/like")
def like_artwork(artwork_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Like an artwork"""
    try:
        # Check if artwork exists
        artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
        if not artwork:
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        # Check if already liked
        existing_like = db.query(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.artwork_id == artwork_id
        ).first()
        
        if existing_like:
            raise HTTPException(status_code=409, detail="Artwork already liked")
        
        # Create new like
        new_like = UserLike(
            user_id=current_user.id,
            artwork_id=artwork_id,
            liked=True
        )
        db.add(new_like)
        db.commit()
        
        return {"message": "Artwork liked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking artwork: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/artworks/{artwork_id}/like")
def unlike_artwork(artwork_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Unlike an artwork"""
    try:
        # Find and delete the like
        like = db.query(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.artwork_id == artwork_id
        ).first()
        
        if not like:
            raise HTTPException(status_code=404, detail="Artwork not liked")
        
        db.delete(like)
        db.commit()
        
        return {"message": "Artwork unliked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking artwork: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Gallery endpoint for random artworks
@app.get("/artworks/gallery")
def get_gallery_artworks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 12,
    sources: Optional[str] = None,
    sort_by: str = "random"
):
    """Get random artworks for the gallery/exhibit page"""
    try:
        # Build base query
        query = db.query(Artwork)
        
        # Apply source filter
        if sources and sources != "all":
            source_list = sources.split(",")
            query = query.filter(Artwork.source.in_(source_list))
        
        # Apply sorting
        if sort_by == "title":
            query = query.order_by(Artwork.title)
        elif sort_by == "artist":
            query = query.order_by(Artwork.artist)
        elif sort_by == "date":
            query = query.order_by(Artwork.date)
        elif sort_by == "source":
            query = query.order_by(Artwork.source)
        else:  # random (default)
            # Use database random function for true randomness
            query = query.order_by(db.func.random())
        
        # Apply pagination
        offset = (page - 1) * limit
        artworks = query.offset(offset).limit(limit).all()
        
        # Check if there are more artworks
        total_count = query.count()
        has_more = (offset + limit) < total_count
        
        return {
            "artworks": artworks,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "has_more": has_more
        }
    except Exception as e:
        logger.error(f"Error getting gallery artworks: {e}")
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
