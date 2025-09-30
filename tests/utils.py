import pytest
import asyncio
import pytest_asyncio
import httpx
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select
from passlib.context import CryptContext


from app.main import app
from app.db.database import Base, get_db
from app.db.models import Bookmark, User
from app.routers.users import get_current_user


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

bcrypt_context = CryptContext(schemes=["bcrypt"])

engine = create_async_engine(TEST_DATABASE_URL,
                             connect_args={"uri": True},
                             echo=False,
                             poolclass=StaticPool)

SessionLocal = async_sessionmaker(bind=engine,
                                  expire_on_commit=False,
                                  class_=AsyncSession)

async def override_get_db():
    async with SessionLocal() as session:
        yield session
        
def override_get_current_user():
    return {"id":1, "sub": "test", "role": "user"}
        
        
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest_asyncio.fixture(scope="function") 
async def db_session():
    async with SessionLocal() as session:
        yield session
    
    
@pytest_asyncio.fixture(scope="session")
async def async_client():
    # === HTTPX TRANSPORT ===
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
    

@pytest_asyncio.fixture(scope="function")
async def seed_data(db_session: AsyncSession):
    # === SEEDING ===
    password_hash = bcrypt_context.hash("x")
    user = User(id=1, email="test@example.com", username="test", hashed_password=password_hash, role="user")
    bookmark = Bookmark(id=1, title="Test", url="https://example.com", favorite=False, owner_id=1)
    db_session.add(user)
    db_session.add(bookmark)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_engine():
    # === SETUP ===
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # === TEARDOWN ===
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)