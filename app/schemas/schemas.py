from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import date

    
class BookmarkResponse(BaseModel):
    id: int
    title: str = Field(max_length=100)
    url: HttpUrl = Field(min_length=1, max_length=2048)
    favorite: bool
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    created_at: date
    
    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = Field(None, max_length=255)


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
    email: str
    username: str
    hashed_password: str
    role: str
    
    class Config:
        from_attributes = True
        
        
class Token(BaseModel):
    access_token: str
    token_type: str