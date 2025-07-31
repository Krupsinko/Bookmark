from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, status, Path, HTTPException
from ..db.database import SessionLocal
from ..db.models import Bookmarks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, HttpUrl
from datetime import date

router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class BookmarkRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = Field(None, max_length=255)
    
    
class BookmarkResponse(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    url: HttpUrl = Field(min_length=1, max_length=2048)
    favorite: bool
    description: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = Field(None, max_length=255)
    created_at: date
    


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[BookmarkResponse])
async def get_all_bookmarks(db: db_dependency):
    return db.query(Bookmarks).all()


@router.get("/{bookmark_id}", status_code=status.HTTP_200_OK, response_model=BookmarkResponse)
async def get_bookmark(db: db_dependency, bookmark_id: int = Path(gt=0)):
    bookmark = db.query(Bookmarks).filter(Bookmarks.id==bookmark_id).first()
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")
    return bookmark
    

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_bookmark(db: db_dependency,
                          bookmark_request: BookmarkRequest):
    bookmark = Bookmarks(**bookmark_request.model_dump(mode="json"))
    db.add(bookmark)
    db.commit()
    db.refresh()
    
    
# @router.put("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_bookmark(db: db_dependency,
#                           request_model: BookmarkRequest):
    

