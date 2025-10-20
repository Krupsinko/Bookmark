from fastapi import FastAPI
from .db.database import engine, Base
from .db.models import User, Bookmark
from .routers import bookmarks, users
import asyncio

app = FastAPI(
    title="BookmarkManager")
# W razie potrzeby stworzenia bazy na nowo - dodać parametr lifespan=lifespan

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.include_router(bookmarks.router)
app.include_router(users.router)