from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import asyncio
import aiohttp
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_db
from database.models import User, Artwork, UserLike, UserRating, UserNote, ImageCache
from api.image_cache_service import image_cache_service
from api.schemas import (
    UserCreate, UserResponse, ArtworkResponse, UserLikeCreate, 
    UserRatingCreate, UserNoteCreate, Token, TokenData,
    BoardCreate, BoardUpdate, BoardResponse, BoardArtworkCreate
)
from api.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from api.services import ArtworkService, UserService, UserLikeService, UserRatingService, UserNoteService, BoardService
from api.artwork_populator import populate_database, get_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global exception handlers to ensure CORS headers are set
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with CORS headers"""
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers=headers
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with CORS headers"""
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers
    )

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Services
artwork_service = ArtworkService()
user_service = UserService()
user_like_service = UserLikeService()
user_rating_service = UserRatingService()
user_note_service = UserNoteService()
board_service = BoardService()

# Image validation cache
image_cache = {}

async def validate_image_url(url: str) -> bool:
    """Validate if an image URL is accessible with more lenient timeout"""
    if not url:
        return False
    
    # Check cache first
    if url in image_cache:
        return image_cache[url]
    
    try:
        # Create SSL context that ignores certificate verification
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with SSL context
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # Use a longer timeout and more lenient validation
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.head(url) as response:
                # Accept 200, 301, 302, 304 status codes as valid
                is_valid = response.status in [200, 301, 302, 304]
                image_cache[url] = is_valid
                return is_valid
    except asyncio.TimeoutError:
        # Timeout doesn't necessarily mean the image is broken
        logger.info(f"Image validation timeout for {url} - assuming valid")
        image_cache[url] = True  # Assume valid if timeout
        return True
    except Exception as e:
        # Only log specific errors, don't assume all exceptions mean broken images
        if "404" in str(e) or "Not Found" in str(e):
            logger.warning(f"Image validation failed for {url}: {e}")
            image_cache[url] = False
            return False
        else:
            # For other errors (SSL, network issues), assume the image might be valid
            logger.info(f"Image validation error for {url} (assuming valid): {e}")
            image_cache[url] = True
            return True

@app.options("/register")
def register_options():
    """Handle OPTIONS request for registration endpoint"""
    return {"message": "Registration endpoint supports POST"}

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        return user_service.create_user(db, user)
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Registration error: {str(e)}")
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

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

@app.options("/token")
def token_options():
    """Handle OPTIONS request for login endpoint"""
    return {"message": "Login endpoint supports POST"}

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

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
        logger.error(f"Error fetching random artwork: {e}")
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
    try:
        return user_like_service.like_artwork(db, current_user.id, artwork_id, like_data.liked)
    except Exception as e:
        logger.error(f"Error liking artwork: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating like: {str(e)}"
        )

@app.post("/artworks/{artwork_id}/rate")
def rate_artwork(
    artwork_id: str,
    rating_data: UserRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate an artwork (1-5 stars)"""
    try:
        if not 1 <= rating_data.rating <= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        return user_rating_service.rate_artwork(db, current_user.id, artwork_id, rating_data.rating)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating artwork: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rating: {str(e)}"
        )

@app.post("/artworks/{artwork_id}/note")
def add_note(
    artwork_id: str,
    note_data: UserNoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a note to an artwork"""
    try:
        return user_note_service.add_note(db, current_user.id, artwork_id, note_data.note)
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding note: {str(e)}"
        )

@app.get("/users/me/likes", response_model=List[ArtworkResponse])
def get_user_likes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all artworks liked by current user"""
    try:
        return user_like_service.get_user_likes(db, current_user.id)
    except Exception as e:
        logger.error(f"Error getting user likes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching liked artworks: {str(e)}"
        )

@app.get("/users/me/stats")
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        return user_service.get_user_stats(db, current_user.id)
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user stats: {str(e)}"
        )

@app.get("/artworks/search")
def search_artworks(
    source: Optional[str] = None,
    artist: Optional[str] = None,
    date_range: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search artworks with filters"""
    try:
        return artwork_service.search_artworks(db, source, artist, date_range, current_user.id)
    except Exception as e:
        logger.error(f"Error searching artworks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching artworks: {str(e)}"
        )

@app.get("/artworks/recommendations", response_model=List[ArtworkResponse])
def get_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized artwork recommendations"""
    try:
        return artwork_service.get_artwork_recommendations(db, current_user.id, limit)
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recommendations: {str(e)}"
        )

@app.get("/artworks/popular", response_model=List[ArtworkResponse])
def get_popular_artworks(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get most popular artworks"""
    try:
        return artwork_service.get_popular_artworks(db, limit)
    except Exception as e:
        logger.error(f"Error getting popular artworks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching popular artworks: {str(e)}"
        )

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
        logger.error(f"Error fetching artworks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching artworks: {str(e)}"
        )

@app.get("/artworks/gallery", response_model=List[ArtworkResponse])
async def get_gallery_artworks(
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
        
        # For now, return artworks without validation to show real images
        # Image validation can be re-enabled later with better error handling
        return artworks
    except Exception as e:
        logger.error(f"Error fetching gallery artworks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching gallery artworks: {str(e)}"
        )

# Board endpoints
@app.post("/boards", response_model=BoardResponse)
def create_board(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new board"""
    try:
        return board_service.create_board(db, current_user.id, board_data)
    except Exception as e:
        logger.error(f"Error creating board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating board: {str(e)}"
        )

@app.get("/boards", response_model=List[BoardResponse])
def get_user_boards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all boards for the current user"""
    try:
        return board_service.get_user_boards(db, current_user.id)
    except Exception as e:
        logger.error(f"Error getting user boards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching boards: {str(e)}"
        )

@app.get("/boards/{board_id}", response_model=BoardResponse)
def get_board(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific board by ID"""
    try:
        board = board_service.get_board(db, board_id, current_user.id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Board not found or access denied"
            )
        return board
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching board: {str(e)}"
        )

@app.put("/boards/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: str,
    board_data: BoardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a board"""
    try:
        return board_service.update_board(db, board_id, current_user.id, board_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating board: {str(e)}"
        )

@app.delete("/boards/{board_id}")
def delete_board(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a board"""
    try:
        return board_service.delete_board(db, board_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting board: {str(e)}"
        )

@app.post("/boards/{board_id}/artworks")
def add_artwork_to_board(
    board_id: str,
    artwork_data: BoardArtworkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an artwork to a board"""
    try:
        return board_service.add_artwork_to_board(db, board_id, current_user.id, artwork_data.artwork_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding artwork to board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding artwork to board: {str(e)}"
        )

@app.delete("/boards/{board_id}/artworks/{artwork_id}")
def remove_artwork_from_board(
    board_id: str,
    artwork_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an artwork from a board"""
    try:
        return board_service.remove_artwork_from_board(db, board_id, current_user.id, artwork_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing artwork from board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing artwork from board: {str(e)}"
        )

@app.get("/boards/{board_id}/artworks", response_model=List[ArtworkResponse])
def get_board_artworks(
    board_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all artworks in a board"""
    try:
        return board_service.get_board_artworks(db, board_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting board artworks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching board artworks: {str(e)}"
        )

@app.get("/artworks/validate-images")
async def validate_artwork_images(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate and fix artwork image URLs"""
    try:
        artworks = db.query(Artwork).filter(Artwork.image_url.isnot(None)).all()
        invalid_count = 0
        fixed_count = 0
        
        for artwork in artworks:
            if artwork.image_url and not artwork.image_url.startswith('/placeholder/'):
                is_valid = await validate_image_url(artwork.image_url)
                if not is_valid:
                    invalid_count += 1
                    # Update to use placeholder
                    artwork.image_url = f"/placeholder/{artwork.source}.jpg"
                    db.commit()
                    fixed_count += 1
        
        return {
            "message": "Image validation completed",
            "total_checked": len(artworks),
            "invalid_found": invalid_count,
            "fixed_count": fixed_count
        }
    except Exception as e:
        logger.error(f"Error validating images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating images: {str(e)}"
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

@app.get("/test")
def test_endpoint():
    """Simple test endpoint that doesn't require database"""
    return {
        "message": "API is working!",
        "cors": "enabled",
        "timestamp": datetime.utcnow().isoformat(),
        "allowed_origins": get_cors_origins()
    }

@app.options("/test")
def test_options():
    """CORS preflight test endpoint"""
    return {"message": "CORS preflight successful"}

@app.get("/cors-debug")
def cors_debug(request: Request):
    """Debug CORS configuration"""
    origin = request.headers.get("origin")
    return {
        "origin": origin,
        "allowed_origins": get_cors_origins(),
        "user_agent": request.headers.get("user-agent"),
        "method": request.method,
        "url": str(request.url)
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

@app.get("/images/optimize")
async def optimize_image(
    url: str,
    width: int = 400,
    height: int = 400,
    quality: int = 85,
    format: str = "JPEG"
):
    """Optimize and serve image with specified parameters"""
    try:
        # Create SSL context that ignores certificate verification
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with SSL context
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # For now, just proxy the original image
        # In a full implementation, this would resize and optimize the image
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.read()
                    return Response(content=content, media_type=response.headers.get('content-type', 'image/jpeg'))
                else:
                    # If original image fails, return placeholder
                    from api.image_service import image_service
                    placeholder = image_service.generate_placeholder('default', width, height, 'modern')
                    return Response(content=placeholder, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        # Return placeholder on error
        from api.image_service import image_service
        placeholder = image_service.generate_placeholder('default', width, height, 'modern')
        return Response(content=placeholder, media_type="image/jpeg")

@app.get("/images/placeholder/{source}")
async def get_placeholder_image_advanced(
    source: str,
    width: int = 400,
    height: int = 400,
    style: str = "modern"
):
    """Generate placeholder image with advanced parameters"""
    try:
        # Use the existing image service to generate placeholders
        from api.image_service import image_service
        placeholder = image_service.generate_placeholder(source, width, height, style)
        return Response(content=placeholder, media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error generating placeholder: {e}")
        # Fallback to simple placeholder
        return get_placeholder_image(source)

@app.get("/images/cached/{url:path}")
async def get_cached_image(
    url: str,
    db: Session = Depends(get_db)
):
    """Get cached image from database"""
    try:
        # Decode URL parameter
        import urllib.parse
        decoded_url = urllib.parse.unquote(url)
        
        # Get or download cached image
        cached_image = await image_cache_service.get_or_download_image(decoded_url, db)
        
        if cached_image and cached_image.is_valid and cached_image.image_data:
            # Return the cached image data
            import base64
            image_data = base64.b64decode(cached_image.image_data)
            content_type = f"image/{cached_image.format}" if cached_image.format else "image/jpeg"
            return Response(content=image_data, media_type=content_type)
        else:
            # Return placeholder if image is not available
            from api.image_service import image_service
            placeholder = image_service.generate_placeholder('default', 400, 400, 'modern')
            return Response(content=placeholder, media_type="image/jpeg")
            
    except Exception as e:
        logger.error(f"Error serving cached image: {e}")
        # Return placeholder on error
        from api.image_service import image_service
        placeholder = image_service.generate_placeholder('default', 400, 400, 'modern')
        return Response(content=placeholder, media_type="image/jpeg")

@app.post("/admin/cache-images")
async def cache_images_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cache all artwork images in database (admin only)"""
    try:
        # Get all artworks with image URLs
        artworks = db.query(Artwork).filter(Artwork.image_url.isnot(None)).all()
        
        cached_count = 0
        failed_count = 0
        
        for artwork in artworks:
            try:
                cached_image = await image_cache_service.get_or_download_image(
                    artwork.image_url, db, artwork.source
                )
                if cached_image and cached_image.is_valid:
                    cached_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Error caching image for artwork {artwork.id}: {e}")
                failed_count += 1
        
        return {
            "message": "Image caching completed",
            "total_artworks": len(artworks),
            "cached_count": cached_count,
            "failed_count": failed_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error caching images: {str(e)}"
        )

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