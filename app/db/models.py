from .database import Base
from sqlalchemy import String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime, timezone

class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) 
    

class Bookmarks(Base):
    __tablename__ = "bookmarks"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[date] = mapped_column(Date, default=datetime.now(timezone.utc))
    
    