import pytest
import asyncio
import pytest_asyncio
import httpx
import os
from dotenv import load_dotenv
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from passlib.context import CryptContext
from freezegun import freeze_time
from datetime import datetime


from app.main import app
from app.db.database import Base, get_db
from app.db.models import Bookmark, User
from app.routers.users import get_current_user


load_dotenv()
TEST_DB_URL = os.getenv("TEST_DB_URL")

bcrypt_context = CryptContext(schemes=["bcrypt"])




@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_engine():
    engine = create_async_engine(url=TEST_DB_URL, echo=False)
    
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
        bind=db_engine,
        expire_on_commit=False,
        class_=AsyncSession
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
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
        
        
        
@pytest_asyncio.fixture(scope="function")
async def seed_data(db_session: AsyncSession):
    # === SEEDING ===
    TEST_DATETIME = datetime(2025, 1, 1, 12, 0, 0)
    password_hash = bcrypt_context.hash("x")
    user = User(email="test@example.com",
                username="test",
                hashed_password=password_hash,
                role="user",
                is_active=True)
    bookmark = Bookmark(title="Test",
                        url="https://example.com",
                        favorite=False,
                        owner_id=1, 
                        created_at=TEST_DATETIME,
                        updated_at=TEST_DATETIME)
    db_session.add(user)
    db_session.add(bookmark)
    await db_session.commit()