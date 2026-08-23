from enum import Enum
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from celery_worker import page_screenshot

from ..db.database import get_db
from ..db.models import Bookmark
from ..schemas.schemas import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkUpdate,
    BookmarkWithOwnerResponse,
    PaginateBookmarkReponse,
)
from .users import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class SortBy(str, Enum):
    CREATED_AT_DESC = "Date descending"
    CREATED_AT_ASC = "Date ascending"
    TITLE_DESC = "Title descending"
    TITLE_ASC = "Title ascending"
    FAVORITE_DESC = "Favorite"
    FAVORITE_ASC = "Not favorite"


# --- GET ALL BOOKMARKS ---
@router.get("/", status_code=status.HTTP_200_OK, response_model=PaginateBookmarkReponse)
async def get_all_bookmarks(
    db: db_dependency,
    user: user_dependency,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: SortBy = Query(SortBy.CREATED_AT_DESC, description="Sort order"),
):
    sort_options = {
        SortBy.CREATED_AT_DESC: Bookmark.created_at.desc(),
        SortBy.CREATED_AT_ASC: Bookmark.created_at.asc(),
        SortBy.TITLE_DESC: Bookmark.title.desc(),
        SortBy.TITLE_ASC: Bookmark.title.asc(),
        SortBy.FAVORITE_DESC: Bookmark.favorite.desc(),
        SortBy.FAVORITE_ASC: Bookmark.favorite.asc(),
    }

    data_stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.owner))
        .where(Bookmark.owner_id == user.get("id"))
        .order_by(sort_options[sort_by])
        .offset(skip)
        .limit(limit)
    )

    count_stmt = (
        select(func.count())
        .select_from(Bookmark)
        .where(Bookmark.owner_id == user.get("id"))
    )

    data_result = await db.execute(data_stmt)
    count_result = await db.execute(count_stmt)

    bookmarks = data_result.scalars().all()
    count = count_result.scalar_one()

    return {
        "total": count,
        "page": (skip // limit) + 1,
        "size": len(bookmarks),
        "items": bookmarks,
    }


# --- GET BOOKMARK ---
@router.get(
    "/{bookmark_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkWithOwnerResponse,
)
async def get_bookmark(
    db: db_dependency, user: user_dependency, bookmark_id: int = Path(gt=0)
):
    stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.owner))
        .where(Bookmark.id == bookmark_id, Bookmark.owner_id == user.get("id"))
    )
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found."
        )
    return bookmark


# --- CREATE BOOKMARKS ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookmarkResponse)
async def create_bookmark(
    db: db_dependency, bookmark_request: BookmarkCreate, user: user_dependency
):
    owner_id = user.get("id")
    s3_key = f"user/{owner_id}/{uuid4()}.png"
    data = bookmark_request.model_dump(mode="json")
    bookmark = Bookmark(**data, owner_id=owner_id, s3_key=s3_key)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    
    page_screenshot.delay(bookmark.url, bookmark.id, s3_key)

    return bookmark


# --- UPDATE BOOKMARK ---
@router.put(
    "/{bookmark_id}", status_code=status.HTTP_200_OK, response_model=BookmarkResponse
)
async def update_bookmark(
    db: db_dependency,
    bookmark_request: BookmarkUpdate,
    user: user_dependency,
    bookmark_id: int = Path(gt=0),
):
    stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.owner))
        .where(Bookmark.id == bookmark_id, Bookmark.owner_id == user.get("id"))
    )
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found."
        )

    for key, value in bookmark_request.model_dump(
        exclude_unset=True, mode="json"
    ).items():  # noqa: E501
        setattr(bookmark, key, value)

    await db.commit()
    await db.refresh(bookmark)
    return bookmark


# --- DELETE BOOKMARK ---
@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    db: db_dependency, user: user_dependency, bookmark_id: int = Path(gt=0)
):
    stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.owner))
        .where(Bookmark.id == bookmark_id, Bookmark.owner_id == user.get("id"))
    )
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found."
        )

    await db.delete(bookmark)
    await db.commit()
