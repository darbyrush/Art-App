from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import json
import random
import logging

from database.models import User, Artwork, UserLike, UserRating, UserNote, APICache
from api.schemas import UserCreate, UserResponse, ArtworkResponse, UserStats
from api.auth import get_password_hash, verify_password
from backend.services.fetchers.random_art import fetch_random_artwork, fetch_artworks_from_sources

# Configure logging
logger = logging.getLogger(__name__)

class UserService:
    def create_user(self, db: Session, user: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise ValueError("Username already registered")
        
        # Create new user
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
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def like_artwork(self, db: Session, user_id: str, artwork_id: str, liked: bool) -> dict:
        """Like or dislike an artwork"""
        # Check if like already exists
        existing_like = db.query(UserLike).filter(
            and_(UserLike.user_id == user_id, UserLike.artwork_id == artwork_id)
        ).first()
        
        if existing_like:
            existing_like.liked = liked
            existing_like.created_at = datetime.utcnow()
        else:
            new_like = UserLike(
                user_id=user_id,
                artwork_id=artwork_id,
                liked=liked
            )
            db.add(new_like)
        
        db.commit()
        return {"message": "Like updated successfully"}
    
    def rate_artwork(self, db: Session, user_id: str, artwork_id: str, rating: int) -> dict:
        """Rate an artwork (1-5 stars)"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if rating already exists
        existing_rating = db.query(UserRating).filter(
            and_(UserRating.user_id == user_id, UserRating.artwork_id == artwork_id)
        ).first()
        
        if existing_rating:
            existing_rating.rating = rating
            existing_rating.updated_at = datetime.utcnow()
        else:
            new_rating = UserRating(
                user_id=user_id,
                artwork_id=artwork_id,
                rating=rating
            )
            db.add(new_rating)
        
        db.commit()
        return {"message": "Rating updated successfully"}
    
    def add_note(self, db: Session, user_id: str, artwork_id: str, note: str) -> dict:
        """Add a note to an artwork"""
        # Check if note already exists
        existing_note = db.query(UserNote).filter(
            and_(UserNote.user_id == user_id, UserNote.artwork_id == artwork_id)
        ).first()
        
        if existing_note:
            existing_note.note = note
            existing_note.updated_at = datetime.utcnow()
        else:
            new_note = UserNote(
                user_id=user_id,
                artwork_id=artwork_id,
                note=note
            )
            db.add(new_note)
        
        db.commit()
        return {"message": "Note updated successfully"}
    
    def get_user_likes(self, db: Session, user_id: str) -> List[ArtworkResponse]:
        """Get all artworks liked by user"""
        liked_artworks = db.query(Artwork).join(UserLike).filter(
            and_(UserLike.user_id == user_id, UserLike.liked == True)
        ).all()
        return [ArtworkResponse.model_validate(artwork) for artwork in liked_artworks]
    
    def get_user_stats(self, db: Session, user_id: str) -> UserStats:
        """Get user statistics"""
        # Total interactions (likes + ratings + notes)
        likes_count = db.query(UserLike).filter(UserLike.user_id == user_id).count()
        ratings_count = db.query(UserRating).filter(UserRating.user_id == user_id).count()
        notes_count = db.query(UserNote).filter(UserNote.user_id == user_id).count()
        total_interactions = likes_count + ratings_count + notes_count
        
        # Liked artworks count
        liked_count = db.query(UserLike).filter(
            and_(UserLike.user_id == user_id, UserLike.liked == True)
        ).count()
        
        # Unique museums
        liked_artworks = db.query(Artwork).join(UserLike).filter(
            and_(UserLike.user_id == user_id, UserLike.liked == True)
        ).all()
        unique_museums = len(set(artwork.source for artwork in liked_artworks))
        
        # Average rating
        ratings = db.query(UserRating).filter(UserRating.user_id == user_id).all()
        avg_rating = sum(rating.rating for rating in ratings) / len(ratings) if ratings else 0
        
        return UserStats(
            total_artworks=total_interactions,
            liked_artworks=liked_count,
            unique_museums=unique_museums,
            avg_rating=avg_rating
        )

class ArtworkService:
    def get_random_artwork(self, db: Session, sources: List[str], user_id: str) -> ArtworkResponse:
        """Get a random artwork with improved diversity and dynamic loading"""
        import logging
        logger = logging.getLogger(__name__)
        
        # First try to get from database with diversity improvements
        from sqlalchemy import func
        existing_artwork = self._get_diverse_artwork(db, sources, user_id)
        
        if existing_artwork:
            return ArtworkResponse.model_validate(existing_artwork)
        
        # If no artwork in database, try to fetch from external APIs
        try:
            from api.artwork_populator import ArtworkPopulator
            populator = ArtworkPopulator()
            
            # Try to populate from one of the requested sources
            for source in sources:
                if source in populator.sources:
                    logger.info(f"Attempting to fetch from {source}...")
                    saved_count = populator.fetch_and_save_from_source(source, populator.sources[source], limit=3)
                    if saved_count > 0:
                        # Try to get the newly saved artwork
                        new_artwork = self._get_diverse_artwork(db, sources, user_id)
                        if new_artwork:
                            return ArtworkResponse.model_validate(new_artwork)
        except Exception as e:
            logger.error(f"Error fetching from external APIs: {e}")
        
        # Fallback to any artwork in database
        sample_artwork = db.query(Artwork).order_by(func.random()).first()
        if sample_artwork:
            return ArtworkResponse.model_validate(sample_artwork)
        
        # If still no artwork, try to populate from all sources
        try:
            logger.info("No artworks found, attempting to populate from all sources...")
            from api.artwork_populator import populate_database
            results = populate_database(artworks_per_source=2)
            
            # Try to get any newly saved artwork
            new_artwork = self._get_diverse_artwork(db, sources, user_id)
            if new_artwork:
                return ArtworkResponse.model_validate(new_artwork)
        except Exception as e:
            logger.error(f"Error populating database: {e}")
        
        raise ValueError("No artwork found - please try again in a moment")
    
    def _get_diverse_artwork(self, db: Session, sources: List[str], user_id: str) -> Optional[Artwork]:
        """Get artwork with diversity improvements"""
        from sqlalchemy import func
        
        # Get user's recently seen artworks to avoid repetition
        recent_artworks = db.query(UserLike.artwork_id).filter(
            and_(UserLike.user_id == user_id, UserLike.created_at >= datetime.utcnow() - timedelta(hours=24))
        ).all()
        recent_ids = [r[0] for r in recent_artworks]
        
        # Build query with diversity filters
        query = db.query(Artwork)
        
        # Filter by sources
        if "all" not in sources:
            query = query.filter(Artwork.source.in_(sources))
        
        # Exclude recently seen artworks
        if recent_ids:
            query = query.filter(~Artwork.id.in_(recent_ids))
        
        # Try to get artwork from less popular sources first
        artwork = query.order_by(func.random()).first()
        
        if not artwork:
            # If no diverse artwork found, get any random artwork
            query = db.query(Artwork)
            if "all" not in sources:
                query = query.filter(Artwork.source.in_(sources))
            artwork = query.order_by(func.random()).first()
        
        return artwork
    
    def get_artwork_recommendations(self, db: Session, user_id: str, limit: int = 10) -> List[ArtworkResponse]:
        """Get personalized artwork recommendations based on user preferences"""
        # Get user's liked sources
        liked_sources = db.query(Artwork.source).join(UserLike).filter(
            and_(UserLike.user_id == user_id, UserLike.liked == True)
        ).distinct().all()
        liked_source_names = [s[0] for s in liked_sources]
        
        # Get artworks from liked sources
        recommendations = db.query(Artwork).filter(
            Artwork.source.in_(liked_source_names)
        ).order_by(func.random()).limit(limit).all()
        
        return [ArtworkResponse.model_validate(artwork) for artwork in recommendations]
    
    def get_popular_artworks(self, db: Session, limit: int = 10) -> List[ArtworkResponse]:
        """Get most popular artworks based on likes"""
        popular_artworks = db.query(Artwork).join(UserLike).filter(
            UserLike.liked == True
        ).group_by(Artwork.id).order_by(func.count(UserLike.id).desc()).limit(limit).all()
        
        return [ArtworkResponse.model_validate(artwork) for artwork in popular_artworks]
    
    def search_artworks(self, db: Session, source: Optional[str], artist: Optional[str], 
                       date_range: Optional[str], user_id: str) -> List[ArtworkResponse]:
        """Search artworks with filters"""
        query = db.query(Artwork)
        
        if source:
            query = query.filter(Artwork.source == source)
        
        if artist:
            query = query.filter(Artwork.artist.ilike(f"%{artist}%"))
        
        if date_range:
            # Simple date range filtering (can be enhanced)
            query = query.filter(Artwork.date.ilike(f"%{date_range}%"))
        
        artworks = query.all()
        return [ArtworkResponse.model_validate(artwork) for artwork in artworks]
    
    def get_artworks(self, db: Session, sources: List[str], offset: int = 0, 
                    limit: int = 20, sort_by: str = "random") -> List[ArtworkResponse]:
        """Get paginated artworks with sorting and filtering"""
        query = db.query(Artwork)
        
        # Filter by sources
        if "all" not in sources:
            query = query.filter(Artwork.source.in_(sources))
        
        # Apply sorting
        if sort_by == "recent":
            query = query.order_by(Artwork.created_at.desc())
        elif sort_by == "popular":
            # Join with likes to sort by popularity
            query = query.join(UserLike).filter(UserLike.liked == True)
            query = query.group_by(Artwork.id).order_by(func.count(UserLike.id).desc())
        elif sort_by == "artist":
            query = query.order_by(Artwork.artist.asc())
        else:  # random
            query = query.order_by(func.random())
        
        # Apply pagination
        artworks = query.offset(offset).limit(limit).all()
        return [ArtworkResponse.model_validate(artwork) for artwork in artworks]
    
    def cache_api_response(self, db: Session, cache_key: str, data: dict, 
                          expires_in_minutes: int = 60) -> None:
        """Cache API response in database"""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        cache_entry = APICache(
            cache_key=cache_key,
            cache_data=json.dumps(data),
            expires_at=expires_at
        )
        
        db.add(cache_entry)
        db.commit()
    
    def get_cached_response(self, db: Session, cache_key: str) -> Optional[dict]:
        """Get cached API response"""
        cache_entry = db.query(APICache).filter(
            and_(
                APICache.cache_key == cache_key,
                APICache.expires_at > datetime.utcnow()
            )
        ).first()
        
        if cache_entry:
            return json.loads(cache_entry.cache_data)
        return None 