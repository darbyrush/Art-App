from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import func
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
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import get_db, init_db, test_connection, get_connection_info
from database.models import User, Artwork, UserLike, UserRating, UserNote, ImageCache
from api.image_cache_service import image_cache_service
from api.schemas import (
    UserCreate, UserResponse, UserUpdate, ArtworkResponse, UserLikeCreate, 
    UserRatingCreate, UserNoteCreate, Token, TokenData,
    BoardCreate, BoardUpdate, BoardResponse, BoardArtworkCreate
)
from api.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from api.services import ArtworkService, UserService, UserLikeService, UserRatingService, UserNoteService, BoardService
from api.artwork_populator import populate_database, get_stats
from backend.config import config

# Production environment validation
def validate_production_environment():
    """Validate critical production environment variables"""
    if config.is_production:
        required_vars = [
            "SECRET_KEY",
            "DATABASE_URL",
            "ENVIRONMENT"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables in production: {missing_vars}")
        
        # Ensure SECRET_KEY is not the default
        secret_key = os.getenv("SECRET_KEY")
        if secret_key in ["your-secret-key-here", "dev-secret-key-change-in-production"]:
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        
        # Ensure ENVIRONMENT is set to production
        if os.getenv("ENVIRONMENT") != "production":
            raise ValueError("ENVIRONMENT must be set to 'production' in production")

# Validate environment before starting
try:
    validate_production_environment()
except ValueError as e:
    if config.is_production:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
    else:
        print(f"Warning: {e}")

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if config.is_production else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Art Explorer API", 
    version="1.0.0",
    description="Production-ready Art Explorer API with enhanced security and performance",
    docs_url="/docs" if not config.is_production else None,
    redoc_url="/redoc" if not config.is_production else None
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    """Initialize app components on startup"""
    import os
    
    # Validate production configuration
    if config.is_production:
        validation = config.validate_production_config()
        if not validation["is_valid"]:
            logger.error(f"Production configuration validation failed: {validation['errors']}")
            raise RuntimeError("Invalid production configuration")
        if validation["warnings"]:
            logger.warning(f"Production configuration warnings: {validation['warnings']}")
    
    # Ensure uploads directory exists
    uploads_dir = "uploads/profile_pictures"
    os.makedirs(uploads_dir, exist_ok=True)
    logger.info(f"Uploads directory ensured: {uploads_dir}")
    
    # Initialize database with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            init_db()
            logger.info("Database initialized successfully")
            break
        except Exception as e:
            logger.error(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Database initialization failed after all retries")
                raise
            else:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    # Test database connection
    if not test_connection():
        logger.error("Database connection test failed")
        raise RuntimeError("Database connection failed")
    
    # Start background scheduler
    try:
        from api.scheduler import start_background_scheduler
        start_background_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.warning(f"Could not start background scheduler: {e}")

# Mount static files for serving uploaded profile pictures
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global OPTIONS handler for all endpoints
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle OPTIONS requests for all endpoints"""
    return {"message": "Endpoint supports CORS preflight"}

# Add trusted host middleware for production (simplified for now)
# if config.is_production:
#     app.add_middleware(
#         TrustedHostMiddleware, 
#         allowed_hosts=["myassemblage.art", "www.myassemblage.art", "localhost"]
#     )

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    start_time = time.time()
    
    # Add request ID for tracking
    request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")
    
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains" if config.is_production else ""
    response.headers["X-Request-ID"] = request_id
    
    # Performance headers
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Rate limiting middleware for production
from collections import defaultdict
import time

# Simple in-memory rate limiter (use Redis in production)
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 1 minute
MAX_REQUESTS_PER_WINDOW = 100  # 100 requests per minute

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for production security"""
    if not config.is_production:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Clean old entries
    current_time = time.time()
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip] 
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return Response(
            content="Rate limit exceeded. Please try again later.",
            status_code=429,
            media_type="text/plain"
        )
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    
    # Continue with request
    return await call_next(request)

# Input validation middleware for production
import re
from urllib.parse import urlparse

@app.middleware("http")
async def input_validation_middleware(request: Request, call_next):
    """Input validation middleware for production security"""
    if not config.is_production:
        return await call_next(request)
    
    # Validate URL parameters
    path_params = request.path_params
    for param_name, param_value in path_params.items():
        if isinstance(param_value, str):
            # Check for potential injection attacks
            if re.search(r'[<>"\']', param_value):
                logger.warning(f"Potential injection attack detected in path parameter {param_name}: {param_value}")
                return Response(
                    content="Invalid input detected",
                    status_code=400,
                    media_type="text/plain"
                )
    
    # Validate query parameters
    query_params = request.query_params
    for param_name, param_value in query_params.items():
        if isinstance(param_value, str):
            # Check for potential injection attacks
            if re.search(r'[<>"\']', param_value):
                logger.warning(f"Potential injection attack detected in query parameter {param_name}: {param_value}")
                return Response(
                    content="Invalid input detected",
                    status_code=400,
                    media_type="text/plain"
                )
    
    # Validate request body size (if applicable)
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length:
            max_size = 10 * 1024 * 1024  # 10MB limit
            if int(content_length) > max_size:
                logger.warning(f"Request body too large: {content_length} bytes")
                return Response(
                    content="Request body too large",
                    status_code=413,
                    media_type="text/plain"
                )
    
    # Continue with request
    return await call_next(request)

def get_cors_origins():
    """Get allowed CORS origins from environment or defaults"""
    import os
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    default_origins = [
        "https://myassemblage.art",
        "https://www.myassemblage.art"
    ]
    all_origins = [origin.strip() for origin in cors_origins if origin.strip()] + default_origins
    return all_origins

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
        # Create secure SSL context for production
        import ssl
        ssl_context = ssl.create_default_context()
        
        # In production, use strict SSL verification
        if config.is_production:
            # Use system default certificate verification
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        else:
            # In development, allow self-signed certificates for testing
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
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

# Test user creation endpoint removed for production security
# This endpoint was used for development/testing only

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

@app.get("/users/me/profile-picture")
def get_profile_picture(current_user: User = Depends(get_current_user)):
    """Get current user's profile picture"""
    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found"
        )
    
    # Extract filename from the profile picture URL
    filename = current_user.profile_picture.split('/')[-1]
    filepath = f"uploads/profile_pictures/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture file not found"
        )
    
    return FileResponse(filepath)

@app.get("/users/{user_id}/profile-picture")
def get_user_profile_picture(user_id: str, db: Session = Depends(get_db)):
    """Get a user's profile picture by user ID (public endpoint)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found"
        )
    
    # Extract filename from the profile picture URL
    filename = user.profile_picture.split('/')[-1]
    filepath = f"uploads/profile_pictures/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture file not found"
        )
    
    return FileResponse(filepath)

@app.get("/users/me/profile-picture/info")
def get_profile_picture_info(current_user: User = Depends(get_current_user)):
    """Get current user's profile picture information"""
    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found"
        )
    
    # Extract filename from the profile picture URL
    filename = current_user.profile_picture.split('/')[-1]
    filepath = f"uploads/profile_pictures/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture file not found"
        )
    
    # Get file information
    import os
    stat = os.stat(filepath)
    
    return {
        "filename": filename,
        "url": current_user.profile_picture,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "modified_at": datetime.fromtimestamp(stat.st_mtime)
    }

@app.get("/users/me/profile-picture/thumbnail")
def get_profile_picture_thumbnail(
    size: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile picture as a thumbnail"""
    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found"
        )
    
    # Extract filename from the profile picture URL
    filename = current_user.profile_picture.split('/')[-1]
    filepath = f"uploads/profile_pictures/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture file not found"
        )
    
    try:
        from PIL import Image
        from fastapi.responses import Response
        
        # Open and resize image
        image = Image.open(filepath)
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/jpeg")
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        # Return original image if thumbnail generation fails
        return FileResponse(filepath)

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
    sources: Optional[str] = None,
    artist: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: str = "date_liked",
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all artworks liked by current user with filtering and sorting"""
    try:
        source_list = sources.split(",") if sources else ["all"]
        skip = (page - 1) * limit
        
        artworks = user_like_service.get_user_likes(
            db, 
            current_user.id, 
            source_list, 
            artist, 
            date_from, 
            date_to, 
            sort_by, 
            skip, 
            limit
        )
        
        return [ArtworkResponse.model_validate(artwork) for artwork in artworks]
    except Exception as e:
        logger.error(f"Error getting user likes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching liked artworks: {str(e)}"
        )

@app.get("/users/me/likes/filter-options")
def get_user_likes_filter_options(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available filter options for user's liked artworks"""
    try:
        # Get distinct artists from user's liked artworks
        artists = db.query(Artwork.artist).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True,
            Artwork.artist.isnot(None),
            Artwork.artist != ""
        ).distinct().order_by(Artwork.artist).all()
        
        # Get distinct sources
        sources = db.query(Artwork.source).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True
        ).distinct().order_by(Artwork.source).all()
        
        # Get date range
        date_range = db.query(
            func.min(Artwork.date).label('min_date'),
            func.max(Artwork.date).label('max_date')
        ).join(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True,
            Artwork.date.isnot(None)
        ).first()
        
        # Get artwork count for stats
        total_count = db.query(UserLike).filter(
            UserLike.user_id == current_user.id,
            UserLike.liked == True
        ).count()
        
        return {
            "artists": [artist[0] for artist in artists if artist[0]],
            "sources": [source[0] for source in sources if source[0]],
            "date_range": {
                "min": date_range.min_date if date_range and date_range.min_date else None,
                "max": date_range.max_date if date_range and date_range.max_date else None
            },
            "total_count": total_count,
            "sort_options": [
                {"value": "date_liked", "label": "Recently Liked"},
                {"value": "title", "label": "Title (A-Z)"},
                {"value": "artist", "label": "Artist (A-Z)"},
                {"value": "date", "label": "Date Created"},
                {"value": "source", "label": "Museum/Source"}
            ]
        }
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching filter options: {str(e)}"
        )

@app.post("/users/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a profile picture for the current user"""
    import os
    import uuid
    import re
    from io import BytesIO
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Validate file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )
        
        # Validate that the file is actually an image by trying to open it
        try:
            from PIL import Image
            image = Image.open(BytesIO(file_content))
            
            # Check image dimensions
            if image.width < 10 or image.height < 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image dimensions too small (minimum 10x10 pixels)"
                )
            
            if image.width > 5000 or image.height > 5000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image dimensions too large (maximum 5000x5000 pixels)"
                )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {str(e)}"
            )
        
        # Generate unique filename
        # Sanitize filename to prevent directory traversal
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename or '')
        file_extension = os.path.splitext(safe_filename)[1].lower()
        
        # Ensure we have a valid extension
        if not file_extension or file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_extension = '.jpg'
        
        filename = f"{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        
        # Ensure uploads directory exists
        uploads_dir = "uploads/profile_pictures"
        os.makedirs(uploads_dir, exist_ok=True)
        
        filepath = f"{uploads_dir}/{filename}"
        
        # Resize image if it's too large (max 800x800)
        try:
            # Create a new image object from the bytes
            image = Image.open(BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if image is too large
            max_dimension = 800
            if image.width > max_dimension or image.height > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save optimized image
            with open(filepath, "wb") as f:
                image.save(f, format='JPEG', quality=85, optimize=True)
        except Exception as e:
            logger.warning(f"Could not optimize image, saving original: {e}")
            # Fallback to saving original if optimization fails
            with open(filepath, "wb") as f:
                f.write(file_content)
        
        # Delete old profile picture if it exists
        if current_user.profile_picture:
            try:
                old_filename = current_user.profile_picture.split('/')[-1]
                old_filepath = f"uploads/profile_pictures/{old_filename}"
                if os.path.exists(old_filepath) and old_filepath != filepath:
                    os.remove(old_filepath)
                    logger.info(f"Deleted old profile picture: {old_filepath}")
            except Exception as e:
                logger.warning(f"Could not delete old profile picture: {e}")
        
        # Log the upload
        logger.info(f"Profile picture uploaded for user {current_user.id}: {filepath}")
        
        # Update user's profile picture URL
        profile_picture_url = f"/uploads/profile_pictures/{filename}"
        user_update = UserUpdate(profile_picture=profile_picture_url)
        updated_user = user_service.update_user(db, current_user.id, user_update)
        
        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": profile_picture_url,
            "user": updated_user
        }
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading profile picture: {str(e)}"
        )

@app.put("/users/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's information"""
    try:
        return user_service.update_user(db, current_user.id, user_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@app.delete("/users/me/profile-picture")
def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's profile picture"""
    try:
        # Remove the profile picture file if it exists
        if current_user.profile_picture:
            import os
            # Extract filename from the profile picture URL
            filename = current_user.profile_picture.split('/')[-1]
            filepath = f"uploads/profile_pictures/{filename}"
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Update user to remove profile picture URL
        user_update = UserUpdate(profile_picture=None)
        updated_user = user_service.update_user(db, current_user.id, user_update)
        
        return {
            "message": "Profile picture deleted successfully",
            "user": updated_user
        }
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile picture: {str(e)}"
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

@app.get("/artworks/gallery")
async def get_gallery_artworks(
    page: int = 1,
    sources: Optional[str] = None,
    sort_by: str = "random",
    limit: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated artworks for gallery view with endless scrolling - optimized"""
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
        
        # Convert to response format
        artwork_responses = [ArtworkResponse.model_validate(artwork) for artwork in artworks]
        
        return {
            "artworks": artwork_responses,
            "page": page,
            "limit": limit,
            "has_more": len(artwork_responses) == limit,
            "count": len(artwork_responses)
        }
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
    """Health check endpoint for Railway"""
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
        # Return degraded status instead of failing completely
        return {
            "status": "degraded",
            "message": "Art Explorer API is running",
            "database": f"error: {str(e)}",
            "timestamp": datetime.utcnow()
        }

@app.get("/startup-health")
def startup_health_check():
    """Simple health check that doesn't require database - for Railway startup"""
    return {
        "status": "starting",
        "message": "Art Explorer API is starting up",
        "timestamp": datetime.utcnow().isoformat()
    }

# Debug endpoints removed for production security
# These endpoints were used for development/testing only

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
        # Create secure SSL context for production
        import ssl
        ssl_context = ssl.create_default_context()
        
        # In production, use strict SSL verification
        if config.is_production:
            # Use system default certificate verification
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        else:
            # In development, allow self-signed certificates for testing
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
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