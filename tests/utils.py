from datetime import datetime
from unittest.mock import patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.database import Base, get_db
from app.db.models import Bookmark, User
from app.main import app
from app.routers.users import get_current_user
from celery_worker import page_screenshot

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

bcrypt_context = CryptContext(schemes=["bcrypt"])


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_engine():
    engine = create_async_engine(url=TEST_DATABASE_URL, echo=False)

    # === SETUP ===
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    # === TEARDOWN ===
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    SessionLocal = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession):
    def override_get_current_user():
        return {"id": 1, "sub": "test", "role": "user"}

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    # === HTTPX TRANSPORT ===
    with patch("app.routers.bookmarks.page_screenshot") as mock_page_screenshot:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client: #HTTPX connects with FastAPI in memory
                     #insted of creating real server
            client.mock_page_screenshot = mock_page_screenshot
            yield client


@pytest_asyncio.fixture(scope="function")
async def seed_data(db_session: AsyncSession):
    # === SEEDING ===
    TEST_DATETIME = datetime(2025, 1, 1, 12, 0, 0)
    password_hash = bcrypt_context.hash("x")
    user = User(
        email="test@example.com",
        username="test",
        hashed_password=password_hash,
        role="user",
        is_active=True,
    )
    bookmark = Bookmark(
        title="Test",
        url="https://example.com",
        favorite=False,
        owner_id=1,
        created_at=TEST_DATETIME,
        updated_at=TEST_DATETIME,
    )
    db_session.add(user)
    db_session.add(bookmark)
    await db_session.commit()
