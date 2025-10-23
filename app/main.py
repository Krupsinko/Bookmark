from fastapi import FastAPI

from .routers import bookmarks, users

app = FastAPI(title="BookmarkManager")
# W razie potrzeby stworzenia bazy na nowo - dodać parametr lifespan=lifespan


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(bookmarks.router)
app.include_router(users.router)
