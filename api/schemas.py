from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None

class ArtworkResponse(BaseModel):
    id: str
    title: str
    artist: Optional[str] = None
    date: Optional[str] = None
    origin: Optional[str] = None
    department: Optional[str] = None
    source: str
    image_url: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLikeCreate(BaseModel):
    liked: bool = True

class UserRatingCreate(BaseModel):
    rating: int

class UserNoteCreate(BaseModel):
    note: str

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

class BoardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class BoardResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    artwork_count: int = 0
    
    class Config:
        from_attributes = True

class BoardArtworkCreate(BaseModel):
    artwork_id: str

class BoardArtworkResponse(BaseModel):
    id: str
    board_id: str
    artwork_id: str
    added_at: datetime
    artwork: ArtworkResponse
    
    class Config:
        from_attributes = True

class BoardWithArtworksResponse(BaseModel):
    board: BoardResponse
    artworks: List[ArtworkResponse] 