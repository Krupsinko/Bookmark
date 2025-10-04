from datetime import date
from sqlalchemy import select

from .utils import *


TEST_DATETIME = "2025-01-01T12:00:00"


@pytest.mark.asyncio
async def test_get_all_bookmarks_authorized(async_client: AsyncClient,
                                            seed_data):
    response = await async_client.get("/bookmarks/", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    
    assert data["total"] == 1
    assert data["page"] == 1
    assert len(data["items"]) == 1
    
    item = data["items"][0]
    assert item["id"] == 1
    assert item["title"] == "Test"
    assert item["url"] == "https://example.com/"
    assert item["created_at"] == TEST_DATETIME
    assert item["updated_at"] == TEST_DATETIME


@pytest.mark.asyncio
async def test_get_bookmark_authorized(async_client: AsyncClient,
                                       seed_data):
    response = await async_client.get("/bookmarks/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["id"] == 1
    assert data["title"] == "Test"
    assert data["url"] == "https://example.com/"
    assert data["owner"] == {"id":1, "username": "test"}
    assert data["created_at"] == TEST_DATETIME
    assert data["updated_at"] == TEST_DATETIME
    
    
    
@pytest.mark.asyncio
@freeze_time("2025-01-01 12:00:00", tz_offset=0)
async def test_create_bookmark(async_client: AsyncClient,
                               db_session):
    request_data = {"title": "Test",
                    "url": "https://example.com/",
                    "description": None,
                    "tags": None,
                    "favorite": False}
    
    response = await async_client.post("/bookmarks/",
                                       json=request_data,
                                       headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Example Domain"
    assert data["url"] == "https://example.com/"
    assert "created_at" in data
    assert "updated_at" in data
    
    
    result = await db_session.execute(select(Bookmark).where(Bookmark.id == data["id"]))
    bookmark = result.scalar_one()
    assert bookmark is not None
    assert bookmark.title == "Example Domain"
    assert bookmark.url == "https://example.com/"
    
    


@pytest.mark.asyncio
async def test_update_bookmark(async_client: AsyncClient,
                               db_session,
                               seed_data):
    request_data = {"title": "Updated title",
                    "url": "https://example.com/",
                    "description": None,
                    "tags": None,}
    
    response = await async_client.put("/bookmarks/1",
                                      json=request_data,
                                      headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    result = await db_session.execute(select(Bookmark).where(Bookmark.id == data["id"]))
    bookmark = result.scalar_one_or_none()
    assert bookmark.title == "Updated title"
    



@pytest.mark.asyncio
async def test_delete_bookmark(async_client: AsyncClient,
                               db_session,
                               seed_data):
    bookmark_id = 1
    
    response = await async_client.delete(f"/bookmarks/{bookmark_id}",
                                         headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    result = await db_session.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    assert result.scalar_one_or_none() == None