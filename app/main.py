from fastapi import FastAPI
from .db.database import engine, Base
from .db.models import Users, Bookmarks
from .routers import bookmarks, users

app = FastAPI(title="BookmarkManager")

Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}

app.include_router(bookmarks.router)
app.include_router(users.router)