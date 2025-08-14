from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Schemas para autenticação
class LoginRequest(BaseModel):
    session_id: str = Field(..., description="Session ID do Instagram")

class LoginResponse(BaseModel):
    status: str
    message: str
    username: Optional[str] = None

# Schemas para contas
class AccountResponse(BaseModel):
    id: int
    username: str
    last_synced: Optional[datetime] = None

class AccountsListResponse(BaseModel):
    status: str
    accounts: List[AccountResponse]

# Schemas para perfis
class ProfileInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    biography: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    is_private: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_business: Optional[bool] = None
    category: Optional[str] = None
    profile_pic_url: Optional[str] = None
    profile_pic_hd: Optional[str] = None
    profile_pic_proxy_url: Optional[str] = None
    external_url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class ProfileResponse(BaseModel):
    success: bool
    data: Optional[ProfileInfo] = None
    message: Optional[str] = None

# Schemas para stories
class StoryInfo(BaseModel):
    id: int
    code: str
    taken_at: datetime
    media_type: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class StoriesResponse(BaseModel):
    status: str
    stories: List[StoryInfo]

# Schemas para posts
class PostsResponse(BaseModel):
    status: str
    posts: List[str]
    source: str

# Schemas para reels
class ReelsResponse(BaseModel):
    status: str
    reels: List[str]
    source: str

# Schemas para privacidade
class PrivacyResponse(BaseModel):
    status: str
    privacy: str
    source: str

# Schemas para respostas de erro
class ErrorResponse(BaseModel):
    status: str
    message: str
    detail: Optional[str] = None

# Schemas para proxy de imagem
class ProxyImageResponse(BaseModel):
    error: Optional[str] = None 