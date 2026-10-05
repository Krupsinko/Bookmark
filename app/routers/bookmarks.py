import boto3

from enum import Enum
from typing import Annotated
from uuid import uuid4

from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from worker.celery_config import celery_app

from ..db.database import get_db
from ..db.models import Bookmark
from ..schemas.schemas import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkUpdate,
    BookmarkWithOwnerResponse,
    PaginateBookmarkReponse,
    ScreenshotUrlResponse
)
from .users import get_current_user
from app.config import AwsSetting

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])

db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

aws_settings = AwsSetting()

s3 = boto3.client("s3")
s3_bucket_name = aws_settings.S3_BUCKET_NAME

class SortBy(str, Enum):
    CREATED_AT_DESC = "Date descending"
    CREATED_AT_ASC = "Date ascending"
    TITLE_DESC = "Title descending"
    TITLE_ASC = "Title ascending"
    FAVORITE_DESC = "Favorite"
    FAVORITE_ASC = "Not favorite"


# --- GET ALL BOOKMARKS ---
@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=PaginateBookmarkReponse
)
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
@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=BookmarkResponse
)
async def create_bookmark(
    db: db_dependency, bookmark_request: BookmarkCreate, user: user_dependency
):
    owner_id = user.get("id")
    s3_key = f"user/{owner_id}/{uuid4()}.png"
    data = bookmark_request.model_dump(mode="json")
    bookmark = Bookmark(**data,
                        owner_id=owner_id,
                        s3_key=s3_key
                        )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)

    celery_app.send_task(
        "bookmark.page_screenshot",
        args=[bookmark.url, s3_key],
    )
    return bookmark


# --- UPDATE BOOKMARK ---
@router.put(
    "/{bookmark_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookmarkResponse
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
        .where(Bookmark.id == bookmark_id,
               Bookmark.owner_id == user.get("id"))
    )
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found."
        )

    for key, value in bookmark_request.model_dump(
        exclude_unset=True,
        mode="json"
    ).items():
        setattr(bookmark, key, value)

    await db.commit()
    await db.refresh(bookmark)
    return bookmark


# --- DELETE BOOKMARK ---
@router.delete("/{bookmark_id}",
               status_code=status.HTTP_204_NO_CONTENT
)
async def delete_bookmark(
    db: db_dependency,
    user: user_dependency,
    bookmark_id: int = Path(gt=0)
):
    stmt = (
        select(Bookmark)
        .options(selectinload(Bookmark.owner))
        .where(Bookmark.id == bookmark_id,
               Bookmark.owner_id == user.get("id"))
    )
    result = await db.execute(stmt)
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found."
        )

    if bookmark.s3_key:
        await run_in_threadpool(
            s3.delete_object,
            Bucket=s3_bucket_name,
            Key=bookmark.s3_key,
        )
    await db.delete(bookmark)
    await db.commit()


# --- GET SCREENSHOT ---
@router.get(
    "/{bookmark_id}/screenshot-url",
    status_code=status.HTTP_200_OK,
    response_model=ScreenshotUrlResponse
)
async def get_screenshot_url(
    db: db_dependency,
    user: user_dependency,
    bookmark_id: int,
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.owner_id == user["id"],
        )
    )
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found.",
        )

    if not bookmark.s3_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot not found.",
        )

    expires_in = 300
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": s3_bucket_name,
            "Key": bookmark.s3_key,
        },
        ExpiresIn=expires_in,
    )

    return ScreenshotUrlResponse(
        url=url,
        expires_in=expires_in,
    )