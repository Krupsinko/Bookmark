from typing import List
from .database import Base
from sqlalchemy import String, Boolean, Date, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date


class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # --- RELATIONS ---
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan") 
    

class Bookmark(Base):
    __tablename__ = "bookmark"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[List[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Date] = mapped_column(Date, default=date.today())
    favicon_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    
    # --- RELATIONS ---
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    owner:  Mapped["User"] = relationship(back_populates="bookmarks")
