from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
import os
import time
import logging
from typing import List, Optional

# Import schemas and models - use correct paths for container
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    title="My Assemblage API",
    description="Simple My Assemblage API - Clean and Working",
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
    logger.info("🚀 Starting My Assemblage API...")
    
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
    
    logger.info("🎉 My Assemblage API startup completed!")

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root endpoint
@app.get("/")
def root_endpoint():
    """Root endpoint - API information"""
    return {
        "message": "My Assemblage API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "My Assemblage API",
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

@app.put("/users/me", response_model=UserResponse)
def update_user_me(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Update current user"""
    try:
        # Update user fields
        if user_update.username is not None:
            current_user.username = user_update.username
        if user_update.email is not None:
            current_user.email = user_update.email
        
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users/me/profile-picture")
def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (5MB limit)
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads/profile_pictures"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{current_user.id}_{int(time.time())}.{file_extension}"
        file_path = os.path.join(uploads_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Update user profile picture URL
        profile_picture_url = f"/uploads/profile_pictures/{filename}"
        current_user.profile_picture = profile_picture_url
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile picture uploaded successfully",
            "user": current_user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/users/me/profile-picture")
def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete profile picture"""
    try:
        if current_user.profile_picture:
            # Remove old file if it exists
            old_file_path = current_user.profile_picture.lstrip('/')
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            
            # Clear profile picture URL
            current_user.profile_picture = None
            db.commit()
            db.refresh(current_user)
        
        return {"message": "Profile picture removed successfully"}
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/stats")
def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user statistics"""
    try:
        # Get liked artworks count
        liked_artworks = db.query(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True
        ).count()
        
        # Get unique museums/sources count
        unique_sources = db.query(Artwork.source).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True
        ).distinct().count()
        
        # Get ratings count
        total_ratings = db.query(UserRating).filter(
            UserRating.user_id == current_user.id
        ).count()
        
        # Get notes count
        total_notes = db.query(UserNote).filter(
            UserNote.user_id == current_user.id
        ).count()
        
        # Get boards count
        total_boards = db.query(Board).filter(
            Board.user_id == current_user.id
        ).count()
        
        return {
            "liked_artworks": liked_artworks,
            "unique_museums": unique_sources,
            "total_ratings": total_ratings,
            "total_notes": total_notes,
            "total_boards": total_boards
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

# Rating endpoints
@app.post("/artworks/{artwork_id}/rate")
def rate_artwork(
    artwork_id: str,
    rating_data: UserRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate an artwork (1-5 stars)"""
    try:
        # Validate rating (1-5 stars)
        if not 1 <= rating_data.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if artwork exists
        artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
        if not artwork:
            raise HTTPException(status_code=404, detail="Artwork not found")
        
        # Check if user already rated this artwork
        existing_rating = db.query(UserRating).filter(
            UserRating.user_id == current_user.id,
            UserRating.artwork_id == artwork_id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_data.rating
            existing_rating.created_at = datetime.utcnow()
        else:
            # Create new rating
            new_rating = UserRating(
                user_id=current_user.id,
                artwork_id=artwork_id,
                rating=rating_data.rating
            )
            db.add(new_rating)
        
        db.commit()
        return {"message": "Rating saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating artwork: {e}")
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
        logger.info(f"Getting liked artworks for user: {current_user.id}, page: {page}, limit: {limit}")
        
        # First check if user has any liked artworks
        user_likes_count = db.query(UserLike).filter(UserLike.user_id == current_user.id).count()
        logger.info(f"User has {user_likes_count} liked artworks")
        
        if user_likes_count == 0:
            # Return empty list if user has no likes
            logger.info("User has no likes, returning empty list")
            return []
        
        # Build query for liked artworks
        logger.info("Building query for liked artworks")
        query = db.query(Artwork).join(UserLike).filter(UserLike.user_id == current_user.id)
        
        # Apply filters
        if sources and sources != "all":
            source_list = sources.split(",")
            query = query.filter(Artwork.source.in_(source_list))
            logger.info(f"Applied source filter: {source_list}")
        
        if artist:
            query = query.filter(Artwork.artist.ilike(f"%{artist}%"))
            logger.info(f"Applied artist filter: {artist}")
        
        if date_from:
            query = query.filter(Artwork.date >= date_from)
            logger.info(f"Applied date from filter: {date_from}")
        
        if date_to:
            query = query.filter(Artwork.date <= date_to)
            logger.info(f"Applied date to filter: {date_to}")
        
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
        
        logger.info(f"Applied sorting: {sort_by}")
        
        # Apply pagination
        offset = (page - 1) * limit
        artworks = query.offset(offset).limit(limit).all()
        logger.info(f"Retrieved {len(artworks)} artworks")
        
        return artworks
    except Exception as e:
        logger.error(f"Error getting liked artworks: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        # Return empty list instead of crashing
        return []

@app.get("/artworks/liked/filters")
def get_liked_artworks_filter_options(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get filter options for liked artworks"""
    try:
        logger.info(f"Getting filter options for user: {current_user.id}")
        
        # First check if user has any liked artworks
        user_likes_count = db.query(UserLike).filter(UserLike.user_id == current_user.id).count()
        logger.info(f"User has {user_likes_count} liked artworks")
        
        if user_likes_count == 0:
            # Return empty filter options if user has no likes
            logger.info("User has no likes, returning empty filter options")
            return {
                "sources": [],
                "artists": [],
                "dateRange": {
                    "min": None,
                    "max": None
                }
            }
        
        # Get unique sources from liked artworks
        logger.info("Querying for unique sources")
        sources_query = db.query(Artwork.source).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            Artwork.source.isnot(None)
        ).distinct()
        sources = sources_query.all()
        source_list = [source[0] for source in sources if source[0]]
        logger.info(f"Found {len(source_list)} unique sources: {source_list}")
        
        # Get unique artists from liked artworks
        logger.info("Querying for unique artists")
        artists_query = db.query(Artwork.artist).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            Artwork.artist.isnot(None)
        ).distinct()
        artists = artists_query.all()
        artist_list = [artist[0] for artist in artists if artist[0]]
        logger.info(f"Found {len(artist_list)} unique artists")
        
        # Get date range from liked artworks
        logger.info("Querying for date range")
        date_range_query = db.query(
            db.func.min(Artwork.date),
            db.func.max(Artwork.date)
        ).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            Artwork.date.isnot(None)
        )
        date_range = date_range_query.first()
        logger.info(f"Date range: {date_range}")
        
        result = {
            "sources": source_list,
            "artists": artist_list,
            "dateRange": {
                "min": date_range[0] if date_range and date_range[0] else None,
                "max": date_range[1] if date_range and date_range[1] else None
            }
        }
        
        logger.info(f"Successfully generated filter options: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        # Return safe default values instead of crashing
        return {
            "sources": [],
            "artists": [],
            "dateRange": {
                "min": None,
                "max": None
            }
        }

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
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 12,
    sources: Optional[str] = None,
    sort_by: str = "random"
):
    """Get random artworks for the gallery/exhibit page (public endpoint)"""
    try:
        logger.info(f"Getting gallery artworks: page={page}, limit={limit}, sources={sources}, sort_by={sort_by}")
        
        # Build base query
        query = db.query(Artwork)
        
        # Check total artwork count
        total_artworks = query.count()
        logger.info(f"Total artworks in database: {total_artworks}")
        
        if total_artworks == 0:
            logger.warning("No artworks found in database")
            return {
                "artworks": [],
                "page": page,
                "limit": limit,
                "total_count": 0,
                "has_more": False
            }
        
        # Apply source filter
        if sources and sources != "all":
            source_list = sources.split(",")
            query = query.filter(Artwork.source.in_(source_list))
            logger.info(f"Applied source filter: {source_list}")
        
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
                            query = query.order_by(func.random())
        
        logger.info(f"Applied sorting: {sort_by}")
        
        # Apply pagination
        offset = (page - 1) * limit
        artworks = query.offset(offset).limit(limit).all()
        logger.info(f"Retrieved {len(artworks)} artworks")
        
        # Check if there are more artworks
        total_count = query.count()
        has_more = (offset + limit) < total_count
        
        result = {
            "artworks": artworks,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "has_more": has_more
        }
        
        logger.info(f"Gallery endpoint result: {len(artworks)} artworks, has_more: {has_more}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting gallery artworks: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Exhibit endpoint for the main landing page
@app.get("/artworks/exhibit")
def get_exhibit_artworks(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 12,
    sources: Optional[str] = None,
    sort_by: str = "random"
):
    """Get artworks for the exhibit page (public endpoint) - optimized for landing page"""
    try:
        logger.info(f"Getting exhibit artworks: page={page}, limit={limit}, sources={sources}, sort_by={sort_by}")
        
        # First, check if database is accessible
        try:
            # Simple test query to check database connection
            test_count = db.query(Artwork).limit(1).count()
            logger.info(f"Database connection test successful, sample count: {test_count}")
        except Exception as db_error:
            logger.error(f"Database connection error: {db_error}")
            # Return a friendly message instead of crashing
            return {
                "artworks": [],
                "page": page,
                "limit": limit,
                "total_count": 0,
                "has_more": False,
                "message": "Database temporarily unavailable. Please try again later."
            }
        
        # Build base query
        query = db.query(Artwork)
        
        # Check total artwork count
        try:
            total_artworks = query.count()
            logger.info(f"Total artworks in database: {total_artworks}")
        except Exception as count_error:
            logger.error(f"Error counting artworks: {count_error}")
            total_artworks = 0
        
        if total_artworks == 0:
            logger.warning("No artworks found in database")
            return {
                "artworks": [],
                "page": page,
                "limit": limit,
                "total_count": 0,
                "has_more": False,
                "message": "No artworks available at the moment. Please check back later."
            }
        
        # Apply source filter
        if sources and sources != "all":
            try:
                source_list = sources.split(",")
                query = query.filter(Artwork.source.in_(source_list))
                logger.info(f"Applied source filter: {source_list}")
            except Exception as filter_error:
                logger.error(f"Error applying source filter: {filter_error}")
                # Continue without filter if it fails
        
        # Apply sorting
        try:
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
                query = query.order_by(func.random())
            
            logger.info(f"Applied sorting: {sort_by}")
        except Exception as sort_error:
            logger.error(f"Error applying sorting: {sort_error}")
            # Default to random if sorting fails
            query = query.order_by(func.random())
        
        # Calculate total count BEFORE applying pagination
        try:
            total_count = query.count()
            logger.info(f"Total artworks after filtering: {total_count}")
        except Exception as count_error:
            logger.error(f"Error counting artworks: {count_error}")
            total_count = 0
        
        # Apply pagination
        try:
            offset = (page - 1) * limit
            artworks = query.offset(offset).limit(limit).all()
            logger.info(f"Retrieved {len(artworks)} artworks")
        except Exception as pagination_error:
            logger.error(f"Error applying pagination: {pagination_error}")
            # Try to get artworks without pagination
            artworks = query.limit(limit).all()
            logger.info(f"Retrieved {len(artworks)} artworks without pagination")
        
        # Check if there are more artworks
        try:
            has_more = (offset + limit) < total_count
            logger.info(f"Pagination: offset={offset}, limit={limit}, total={total_count}, has_more={has_more}")
        except Exception as count_error:
            logger.error(f"Error checking for more artworks: {count_error}")
            has_more = len(artworks) == limit  # Assume more if we got a full page
        
        result = {
            "artworks": artworks,
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "has_more": has_more
        }
        
        logger.info(f"Exhibit endpoint result: {len(artworks)} artworks, has_more: {has_more}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting exhibit artworks: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        
        # Return a graceful error response instead of crashing
        return {
            "artworks": [],
            "page": page,
            "limit": limit,
            "total_count": 0,
            "has_more": False,
            "error": "Failed to load artworks. Please try again later.",
            "message": "We're experiencing technical difficulties. Please refresh the page or try again later."
        }

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
