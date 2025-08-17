from fastapi import FastAPI
from .db.database import engine, Base
from .db.models import User, Bookmark
from .routers import bookmarks, users
from contextlib import asynccontextmanager
import asyncio


# async def create_tables():
#     async with engine.begin() as connection:
#         await connection.run_sync(Base.metadata.create_all)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await create_tables()
#     yield


app = FastAPI(
    title="BookmarkManager")
# W razie potrzeby stworzenia bazy na nowo - dodać parametr lifespan=lifespan

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.include_router(bookmarks.router)
app.include_router(users.router)