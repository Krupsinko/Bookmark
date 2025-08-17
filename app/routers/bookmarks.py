from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.database import get_db
from ..db.models import Bookmark 
from ..schemas.schemas import BookmarkResponse, BookmarkCreate, BookmarkUpdate
from .users import get_current_user
from ..utils.scraper import scrape_title, scrape_favicon



router = APIRouter(
    prefix="/bookmarks",
    tags=["Bookmarks"]
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[BookmarkResponse])
async def get_all_bookmarks(db: db_dependency,
                            user: user_dependency):
    stmt = select(Bookmark).where(Bookmark.owner_id == user.get("id"))
    result = await db.execute(stmt)
    bookmarks = result.scalars().all()
    return bookmarks




@router.get("/{bookmark_id}", status_code=status.HTTP_200_OK, response_model=BookmarkResponse)
async def get_bookmark(db: db_dependency,
                       user: user_dependency, 
                       bookmark_id: int = Path(gt=0)):
    
    stmt = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.owner_id == user.get("id"))
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()
    
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")
    return bookmark
    



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookmarkResponse)
async def create_bookmark(db: db_dependency,
                          bookmark_request: BookmarkCreate,
                          user: user_dependency):
    title_tag = await scrape_title(str(bookmark_request.url))
    data = bookmark_request.model_dump(mode="json")
    data.pop("title", None)
    bookmark = Bookmark(**data,
                        owner_id=user.get("id"),
                        title=title_tag
    )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark
    
    
    
    
@router.put("/{bookmark_id}", status_code=status.HTTP_200_OK, response_model=BookmarkResponse)
async def update_bookmark(db: db_dependency, 
                          bookmark_request: BookmarkUpdate,
                          user: user_dependency, 
                          bookmark_id: int = Path(gt=0)):
    
    stmt = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.owner_id == user.get("id"))
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()
    
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")
    
    for key, value in bookmark_request.model_dump(exclude_unset=True, mode="json").items():
        setattr(bookmark, key, value)
    
    await db.commit()
    await db.refresh(bookmark)
    return bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(db: db_dependency,
                          user: user_dependency,
                          bookmark_id: int = Path(gt=0)
                          ):
    stmt = select(Bookmark).where(Bookmark.id == bookmark_id,
                                  Bookmark.owner_id == user.get("id"))
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()
    
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")
    
    await db.delete(bookmark)
    await db.commit()
    