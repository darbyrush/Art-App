from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json

from database.config import get_db, init_db
from database.models import User, Artwork, UserLike, UserRating, UserNote, APICache
from api.schemas import (
    UserCreate, UserResponse, ArtworkResponse, UserLikeCreate, 
    UserRatingCreate, UserNoteCreate, Token, TokenData
)
from api.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from api.services import ArtworkService, UserService
from api.artwork_populator import populate_database, get_stats

# Initialize database
init_db()

app = FastAPI(title="Art Explorer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Services
artwork_service = ArtworkService()
user_service = UserService()

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return user_service.create_user(db, user)

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/artworks/random", response_model=ArtworkResponse)
def get_random_artwork(
    sources: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a random artwork from specified sources"""
    source_list = sources.split(",") if sources else ["all"]
    return artwork_service.get_random_artwork(db, source_list, current_user.id)

@app.post("/artworks/{artwork_id}/like")
def like_artwork(
    artwork_id: str,
    like_data: UserLikeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like or dislike an artwork"""
    return user_service.like_artwork(db, current_user.id, artwork_id, like_data.liked)

@app.post("/artworks/{artwork_id}/rate")
def rate_artwork(
    artwork_id: str,
    rating_data: UserRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate an artwork (1-5 stars)"""
    return user_service.rate_artwork(db, current_user.id, artwork_id, rating_data.rating)

@app.post("/artworks/{artwork_id}/note")
def add_note(
    artwork_id: str,
    note_data: UserNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a note to an artwork"""
    return user_service.add_note(db, current_user.id, artwork_id, note_data.note)

@app.get("/users/me/likes", response_model=List[ArtworkResponse])
def get_user_likes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all artworks liked by current user"""
    return user_service.get_user_likes(db, current_user.id)

@app.get("/users/me/stats")
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    return user_service.get_user_stats(db, current_user.id)

@app.get("/artworks/search")
def search_artworks(
    source: Optional[str] = None,
    artist: Optional[str] = None,
    date_range: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search artworks with filters"""
    return artwork_service.search_artworks(db, source, artist, date_range, current_user.id)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/admin/populate-database")
def populate_database_endpoint(
    artworks_per_source: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Populate database with artworks from external APIs (admin only)"""
    try:
        results = populate_database(artworks_per_source)
        return {
            "message": "Database populated successfully",
            "results": results,
            "total_added": sum(results.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error populating database: {str(e)}"
        )

@app.get("/admin/database-stats")
def get_database_stats(current_user: User = Depends(get_current_user)):
    """Get database statistics (admin only)"""
    try:
        stats = get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting database stats: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 