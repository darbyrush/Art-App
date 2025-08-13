import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, text
from api.database.models import User, Artwork, UserLike, UserRating, UserNote, Board, BoardArtwork, ImageCache
from api.schemas import UserCreate, UserResponse, UserUpdate, ArtworkResponse, BoardCreate, BoardUpdate, BoardResponse, BoardArtworkCreate, BoardArtworkResponse
from api.auth import get_password_hash, verify_password
from api.cache import cache_user_by_username, cache_artwork_by_id, invalidate_user_cache, invalidate_artwork_cache
from datetime import datetime, timedelta
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class UserService:
    def create_user(self, db: Session, user: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return UserResponse.model_validate(db_user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise

    @cache_user_by_username(ttl=600)
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username with caching"""
        return db.query(User).filter(User.username == username).first()

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = self.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, db: Session, user_id: str, user_update: UserUpdate) -> UserResponse:
        """Update user information"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Update only provided fields
            if user_update.username is not None:
                # Check if username is already taken
                existing_user = db.query(User).filter(
                    User.username == user_update.username,
                    User.id != user_id
                ).first()
                if existing_user:
                    raise ValueError("Username already taken")
                user.username = user_update.username
            
            if user_update.email is not None:
                # Check if email is already taken
                existing_user = db.query(User).filter(
                    User.email == user_update.email,
                    User.id != user_id
                ).first()
                if existing_user:
                    raise ValueError("Email already taken")
                user.email = user_update.email
            
            if user_update.profile_picture is not None:
                user.profile_picture = user_update.profile_picture
            
            db.commit()
            db.refresh(user)
            return UserResponse.model_validate(user)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise

    def get_user_stats(self, db: Session, user_id: str) -> Dict:
        """Get user statistics"""
        try:
            # Count liked artworks
            liked_count = db.query(UserLike).filter(
                UserLike.user_id == user_id,
                UserLike.liked == True
            ).count()
            
            # Count unique museums from liked artworks
            unique_museums = db.query(Artwork.source).join(
                UserLike, Artwork.id == UserLike.artwork_id
            ).filter(
                UserLike.user_id == user_id,
                UserLike.liked == True
            ).distinct().count()
            
            # Count total ratings
            ratings_count = db.query(UserRating).filter(
                UserRating.user_id == user_id
            ).count()
            
            # Count total notes
            notes_count = db.query(UserNote).filter(
                UserNote.user_id == user_id
            ).count()
            
            # Count user's boards
            boards_count = db.query(Board).filter(
                Board.user_id == user_id
            ).count()
            
            return {
                "liked_artworks": liked_count,
                "unique_museums": unique_museums,
                "total_ratings": ratings_count,
                "total_notes": notes_count,
                "total_boards": boards_count
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            # Return default stats on error
            return {
                "liked_artworks": 0,
                "unique_museums": 0,
                "total_ratings": 0,
                "total_notes": 0,
                "total_boards": 0
            }

class ArtworkService:
    def get_artworks(self, db: Session, sources: List[str] = None, skip: int = 0, limit: int = 100, sort_by: str = "random") -> List[Artwork]:
        """Get artworks with pagination, filtering, and sorting - optimized"""
        query = db.query(Artwork)
        
        # Apply source filtering if specified
        if sources and "all" not in sources:
            query = query.filter(Artwork.source.in_(sources))
        
        # Apply sorting - optimize random queries for large datasets
        if sort_by == "random":
            # For PostgreSQL, use a more efficient random sampling method
            # Get total count first, then use offset with random number
            total_count = query.count()
            if total_count > limit:
                import random
                max_offset = max(0, total_count - limit)
                random_offset = random.randint(0, max_offset)
                query = query.offset(random_offset).limit(limit)
            else:
                query = query.order_by(func.random()).limit(limit)
        elif sort_by == "title":
            query = query.order_by(Artwork.title).offset(skip).limit(limit)
        elif sort_by == "date":
            query = query.order_by(Artwork.date).offset(skip).limit(limit)
        elif sort_by == "artist":
            query = query.order_by(Artwork.artist).offset(skip).limit(limit)
        else:
            query = query.offset(skip).limit(limit)
        
        return query.all()

    @cache_artwork_by_id(ttl=1800)
    def get_artwork_by_id(self, db: Session, artwork_id: str) -> Optional[Artwork]:
        """Get artwork by ID with caching"""
        return db.query(Artwork).filter(Artwork.id == artwork_id).first()

    def get_random_artwork(self, db: Session, sources: Optional[str] = None) -> Optional[Artwork]:
        """Get a random artwork"""
        query = db.query(Artwork)
        if sources and sources != "all":
            source_list = sources.split(",")
            query = query.filter(Artwork.source.in_(source_list))
        return query.order_by(func.random()).first()

class UserLikeService:
    def like_artwork(self, db: Session, user_id: str, artwork_id: str, liked: bool = True) -> bool:
        """Like or unlike an artwork"""
        try:
            # Check if like already exists
            existing_like = db.query(UserLike).filter(
                UserLike.user_id == user_id,
                UserLike.artwork_id == artwork_id
            ).first()
            
            if existing_like:
                existing_like.liked = liked
            else:
                new_like = UserLike(
                    user_id=user_id,
                    artwork_id=artwork_id,
                    liked=liked
                )
                db.add(new_like)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error liking artwork: {e}")
            return False

    def get_user_likes(self, db: Session, user_id: str, sources: List[str] = None, 
                      artist: str = None, date_from: str = None, date_to: str = None,
                      sort_by: str = "date_liked", skip: int = 0, limit: int = 100) -> List[Artwork]:
        """Get all artworks liked by user with filtering and sorting"""
        query = db.query(Artwork).join(UserLike).filter(
            UserLike.user_id == user_id,
            UserLike.liked == True
        )
        
        # Apply source filtering
        if sources and "all" not in sources:
            query = query.filter(Artwork.source.in_(sources))
        
        # Apply artist filtering
        if artist:
            query = query.filter(Artwork.artist.ilike(f"%{artist}%"))
        
        # Apply date filtering
        if date_from:
            query = query.filter(Artwork.date >= date_from)
        if date_to:
            query = query.filter(Artwork.date <= date_to)
        
        # Apply sorting
        if sort_by == "date_liked":
            query = query.order_by(UserLike.created_at.desc())
        elif sort_by == "title":
            query = query.order_by(Artwork.title)
        elif sort_by == "artist":
            query = query.order_by(Artwork.artist)
        elif sort_by == "date":
            query = query.order_by(Artwork.date.desc())
        elif sort_by == "source":
            query = query.order_by(Artwork.source)
        else:
            query = query.order_by(UserLike.created_at.desc())
        
        return query.offset(skip).limit(limit).all()

class UserRatingService:
    def rate_artwork(self, db: Session, user_id: str, artwork_id: str, rating: int) -> bool:
        """Rate an artwork"""
        try:
            # Check if rating already exists
            existing_rating = db.query(UserRating).filter(
                UserRating.user_id == user_id,
                UserRating.artwork_id == artwork_id
            ).first()
            
            if existing_rating:
                existing_rating.rating = rating
            else:
                new_rating = UserRating(
                    user_id=user_id,
                    artwork_id=artwork_id,
                    rating=rating
                )
                db.add(new_rating)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error rating artwork: {e}")
            return False

class UserNoteService:
    def add_note(self, db: Session, user_id: str, artwork_id: str, note: str) -> bool:
        """Add a note to an artwork"""
        try:
            new_note = UserNote(
                user_id=user_id,
                artwork_id=artwork_id,
                note=note
            )
            db.add(new_note)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding note: {e}")
            return False

class BoardService:
    def create_board(self, db: Session, user_id: str, board_data: BoardCreate) -> BoardResponse:
        """Create a new board for a user"""
        try:
            db_board = Board(
                user_id=user_id,
                name=board_data.name,
                description=board_data.description,
                is_public=board_data.is_public
            )
            db.add(db_board)
            db.commit()
            db.refresh(db_board)
            return BoardResponse.model_validate(db_board)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating board: {e}")
            raise

    def get_user_boards(self, db: Session, user_id: str) -> List[BoardResponse]:
        """Get all boards for a user"""
        try:
            boards = db.query(Board).filter(Board.user_id == user_id).all()
            return [BoardResponse.model_validate(board) for board in boards]
        except Exception as e:
            logger.error(f"Error getting user boards: {e}")
            raise

    def get_board(self, db: Session, board_id: str, user_id: str) -> Optional[BoardResponse]:
        """Get a specific board"""
        try:
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            return BoardResponse.model_validate(board) if board else None
        except Exception as e:
            logger.error(f"Error getting board: {e}")
            raise

    def update_board(self, db: Session, board_id: str, user_id: str, board_data: BoardUpdate) -> Optional[BoardResponse]:
        """Update a board"""
        try:
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            
            if not board:
                return None
            
            if board_data.name is not None:
                board.name = board_data.name
            if board_data.description is not None:
                board.description = board_data.description
            if board_data.is_public is not None:
                board.is_public = board_data.is_public
            
            board.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(board)
            return BoardResponse.model_validate(board)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating board: {e}")
            raise

    def delete_board(self, db: Session, board_id: str, user_id: str) -> bool:
        """Delete a board"""
        try:
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            
            if not board:
                return False
            
            db.delete(board)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting board: {e}")
            return False

    def add_artwork_to_board(self, db: Session, board_id: str, user_id: str, artwork_id: str) -> bool:
        """Add an artwork to a board"""
        try:
            # Verify board belongs to user
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            
            if not board:
                return False
            
            # Check if artwork already in board
            existing = db.query(BoardArtwork).filter(
                BoardArtwork.board_id == board_id,
                BoardArtwork.artwork_id == artwork_id
            ).first()
            
            if existing:
                return True  # Already exists
            
            board_artwork = BoardArtwork(
                board_id=board_id,
                artwork_id=artwork_id
            )
            db.add(board_artwork)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding artwork to board: {e}")
            return False

    def remove_artwork_from_board(self, db: Session, board_id: str, user_id: str, artwork_id: str) -> bool:
        """Remove an artwork from a board"""
        try:
            # Verify board belongs to user
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            
            if not board:
                return False
            
            board_artwork = db.query(BoardArtwork).filter(
                BoardArtwork.board_id == board_id,
                BoardArtwork.artwork_id == artwork_id
            ).first()
            
            if not board_artwork:
                return False
            
            db.delete(board_artwork)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error removing artwork from board: {e}")
            return False

    def get_board_artworks(self, db: Session, board_id: str, user_id: str) -> List[Artwork]:
        """Get all artworks in a board"""
        try:
            # Verify board belongs to user
            board = db.query(Board).filter(
                Board.id == board_id,
                Board.user_id == user_id
            ).first()
            
            if not board:
                return []
            
            return db.query(Artwork).join(BoardArtwork).filter(
                BoardArtwork.board_id == board_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting board artworks: {e}")
            raise

class ImageCacheService:
    def get_cached_image(self, db: Session, original_url: str) -> Optional[ImageCache]:
        """Get cached image by original URL"""
        try:
            return db.query(ImageCache).filter(ImageCache.original_url == original_url).first()
        except Exception as e:
            logger.error(f"Error getting cached image: {e}")
            return None

    def cache_image(self, db: Session, image_data: Dict) -> ImageCache:
        """Cache image validation result"""
        try:
            # Check if already cached
            existing = db.query(ImageCache).filter(
                ImageCache.original_url == image_data['url']
            ).first()
            
            if existing:
                # Update existing cache
                existing.is_valid = image_data.get('valid', False)
                existing.width = image_data.get('width')
                existing.height = image_data.get('height')
                existing.format = image_data.get('format')
                existing.size_bytes = image_data.get('size_bytes')
                existing.error_message = image_data.get('error')
                existing.last_validated = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
            else:
                # Create new cache entry
                existing = ImageCache(
                    original_url=image_data['url'],
                    is_valid=image_data.get('valid', False),
                    width=image_data.get('width'),
                    height=image_data.get('height'),
                    format=image_data.get('format'),
                    size_bytes=image_data.get('size_bytes'),
                    error_message=image_data.get('error'),
                    source=image_data.get('source')
                )
                db.add(existing)
            
            db.commit()
            db.refresh(existing)
            return existing
        except Exception as e:
            db.rollback()
            logger.error(f"Error caching image: {e}")
            raise

    def get_valid_images_for_source(self, db: Session, source: str) -> List[ImageCache]:
        """Get all valid cached images for a source"""
        try:
            return db.query(ImageCache).filter(
                ImageCache.source == source,
                ImageCache.is_valid == True
            ).all()
        except Exception as e:
            logger.error(f"Error getting valid images for source: {e}")
            return []

    def cleanup_old_cache(self, db: Session, days: int = 30) -> int:
        """Clean up old cache entries"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = db.query(ImageCache).filter(
                ImageCache.last_validated < cutoff_date
            ).delete()
            db.commit()
            return deleted
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up cache: {e}")
            return 0

# Service instances
user_service = UserService()
artwork_service = ArtworkService()
user_like_service = UserLikeService()
user_rating_service = UserRatingService()
user_note_service = UserNoteService()
board_service = BoardService()
image_cache_service = ImageCacheService() 