from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    likes = relationship("UserLike", back_populates="user")
    ratings = relationship("UserRating", back_populates="user")
    notes = relationship("UserNote", back_populates="user")

class Artwork(Base):
    __tablename__ = "artworks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    artist = Column(String(200), nullable=True)
    date = Column(String(100), nullable=True)
    origin = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    source = Column(String(100), nullable=False)  # museum source
    image_url = Column(Text, nullable=True)
    external_id = Column(String(100), nullable=True)  # ID from external API
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    likes = relationship("UserLike", back_populates="artwork")
    ratings = relationship("UserRating", back_populates="artwork")
    notes = relationship("UserNote", back_populates="artwork")

class UserLike(Base):
    __tablename__ = "user_likes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    liked = Column(Boolean, default=True)  # True for like, False for dislike
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    artwork = relationship("Artwork", back_populates="likes")

class UserRating(Base):
    __tablename__ = "user_ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    artwork = relationship("Artwork", back_populates="ratings")

class UserNote(Base):
    __tablename__ = "user_notes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    artwork_id = Column(String, ForeignKey("artworks.id"), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    artwork = relationship("Artwork", back_populates="notes")

class APICache(Base):
    __tablename__ = "api_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_data = Column(Text, nullable=False)  # JSON string
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 