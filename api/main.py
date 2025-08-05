from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Start background scheduler
try:
    from api.scheduler import start_background_scheduler
    start_background_scheduler()
except Exception as e:
    print(f"Warning: Could not start background scheduler: {e}")

app = FastAPI(title="Art Explorer API", version="1.0.0")

# Import CORS configuration
from api.cors_config import get_cors_origins, DynamicCORSMiddleware

# Add CORS middleware - Railway deployment test
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DynamicCORSMiddleware)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Services
artwork_service = ArtworkService()
user_service = UserService()

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return user_service.create_user(db, user)

@app.post("/create-test-user", response_model=UserResponse)
def create_test_user(db: Session = Depends(get_db)):
    """Create a test user for development"""
    try:
        test_user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        return user_service.create_user(db, test_user_data)
    except ValueError as e:
        if "already registered" in str(e):
            # User already exists, return existing user
            existing_user = db.query(User).filter(User.username == "testuser").first()
            if existing_user:
                return UserResponse.model_validate(existing_user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating test user: {str(e)}"
        )

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
    try:
        source_list = sources.split(",") if sources else ["all"]
        return artwork_service.get_random_artwork(db, source_list, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching artwork: {str(e)}"
        )

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

@app.get("/artworks/recommendations", response_model=List[ArtworkResponse])
def get_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized artwork recommendations"""
    return artwork_service.get_artwork_recommendations(db, current_user.id, limit)

@app.get("/artworks/popular", response_model=List[ArtworkResponse])
def get_popular_artworks(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get most popular artworks"""
    return artwork_service.get_popular_artworks(db, limit)

@app.get("/artworks", response_model=List[ArtworkResponse])
def get_artworks(
    page: int = 1,
    sources: Optional[str] = None,
    sort_by: str = "random",
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated artworks with filters"""
    try:
        source_list = sources.split(",") if sources else ["all"]
        offset = (page - 1) * limit
        
        artworks = artwork_service.get_artworks(
            db, 
            source_list, 
            offset, 
            limit, 
            sort_by
        )
        return artworks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching artworks: {str(e)}"
        )

@app.get("/artworks/gallery", response_model=List[ArtworkResponse])
def get_gallery_artworks(
    page: int = 1,
    sources: Optional[str] = None,
    sort_by: str = "random",
    limit: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated artworks for gallery view with endless scrolling"""
    try:
        source_list = sources.split(",") if sources else ["all"]
        offset = (page - 1) * limit
        
        artworks = artwork_service.get_artworks(
            db, 
            source_list, 
            offset, 
            limit, 
            sort_by
        )
        return artworks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching gallery artworks: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy", 
            "message": "Art Explorer API is running",
            "database": "connected",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": "Art Explorer API is running",
            "database": f"error: {str(e)}",
            "timestamp": datetime.utcnow()
        }

@app.get("/placeholder/{source}.jpg")
def get_placeholder_image(source: str):
    """Generate a placeholder image for missing artwork images"""
    try:
        # Create a simple placeholder image
        width, height = 400, 400
        img = Image.new('RGB', (width, height), color='#f3f4f6')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Add text
        text = f"Artwork\n{source.title()}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#6b7280', font=font)
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        from fastapi.responses import Response
        return Response(content=img_byte_arr.getvalue(), media_type="image/jpeg")
    except Exception as e:
        # Return a simple error response if image generation fails
        return {"error": "Could not generate placeholder image"}

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
        from api.background_tasks import background_manager
        return background_manager.get_database_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting database stats: {str(e)}"
        )

@app.post("/admin/trigger-population")
def trigger_population(current_user: User = Depends(get_current_user)):
    """Manually trigger database population (admin only)"""
    try:
        from api.background_tasks import background_manager
        result = background_manager.populate_database_background()
        return {
            "message": "Database population triggered successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering population: {str(e)}"
        )

@app.post("/admin/cleanup")
def cleanup_database(current_user: User = Depends(get_current_user)):
    """Clean up old artworks (admin only)"""
    try:
        from api.background_tasks import background_manager
        deleted_count = background_manager.cleanup_old_artworks()
        return {
            "message": "Database cleanup completed",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up database: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 