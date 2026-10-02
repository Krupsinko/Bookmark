from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..config import DatabaseSettings

db_settings = DatabaseSettings()
ASYNC_DATABASE_URL = db_settings.DATABASE_URL

async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    autoflush=False, bind=async_engine, class_=AsyncSession
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
