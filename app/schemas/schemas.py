from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime

    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    
    
class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    id: int
    title: str = Field(max_length=100)
    url: HttpUrl = Field(min_length=1, max_length=2048)
    favorite: bool
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    created_at: datetime
    
    
class PaginateBookmarkReponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[BookmarkResponse]    

    
class BookmarkWithOwnerResponse(BookmarkResponse):
    owner: UserResponse    

    
class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = Field(None, max_length=255)
    favorite: bool = Field(True)


class BookmarkUpdate(BaseModel):
    url: HttpUrl
    title: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = Field(None, max_length=255)
        
        
class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str
    role: str
    
    
class CreateUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    username: str
    hashed_password: str
    role: str
        
        
class Token(BaseModel):
    access_token: str
    token_type: str