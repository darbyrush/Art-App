from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    likes = relationship("UserLike", back_populates="user")
    ratings = relationship("UserRating", back_populates="user")
    notes = relationship("UserNote", back_populates="user")
    boards = relationship("Board", back_populates="user")

class Artwork(Base):
    __tablename__ = "artworks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    artist = Column(String(200), nullable=True)
    date = Column(String(100), nullable=True)
    origin = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    source = Column(String(50), nullable=False)
    image_url = Column(Text, nullable=True)
    external_id = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    likes = relationship("UserLike", back_populates="artwork")
    ratings = relationship("UserRating", back_populates="artwork")
    notes = relationship("UserNote", back_populates="artwork")
    board_artworks = relationship("BoardArtwork", back_populates="artwork")

class UserLike(Base):
    __tablename__ = "user_likes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    liked = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="likes")
    artwork = relationship("Artwork", back_populates="likes")

class UserRating(Base):
    __tablename__ = "user_ratings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="ratings")
    artwork = relationship("Artwork", back_populates="ratings")

class UserNote(Base):
    __tablename__ = "user_notes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notes")
    artwork = relationship("Artwork", back_populates="notes")

class Board(Base):
    __tablename__ = "boards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="boards")
    board_artworks = relationship("BoardArtwork", back_populates="board")

class BoardArtwork(Base):
    __tablename__ = "board_artworks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    board = relationship("Board", back_populates="board_artworks")
    artwork = relationship("Artwork", back_populates="board_artworks")

class ImageCache(Base):
    __tablename__ = "image_cache"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_url = Column(Text, nullable=False, unique=True)
    validated_url = Column(Text, nullable=True)  # URL after validation/optimization
    image_data = Column(Text, nullable=True)  # Base64 encoded image data
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String(20), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    is_valid = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)  # Which art source this belongs to
    last_validated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 