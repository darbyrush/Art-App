from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None  # Changed from EmailStr to str to allow empty strings

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ArtworkBase(BaseModel):
    title: str
    artist: Optional[str] = None
    date: Optional[str] = None
    origin: Optional[str] = None
    department: Optional[str] = None
    source: str
    image_url: Optional[str] = None
    external_id: Optional[str] = None

class ArtworkResponse(ArtworkBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLikeCreate(BaseModel):
    liked: bool = True

class UserRatingCreate(BaseModel):
    rating: int  # 1-5 stars

class UserNoteCreate(BaseModel):
    note: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserStats(BaseModel):
    total_artworks: int
    liked_artworks: int
    unique_museums: int
    avg_rating: float

class SearchFilters(BaseModel):
    source: Optional[str] = None
    artist: Optional[str] = None
    date_range: Optional[str] = None 