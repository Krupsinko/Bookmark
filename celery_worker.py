import hashlib
import os

from celery import Celery
from playwright.sync_api import Playwright, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from sqlalchemy import select

from app.db.database import SyncSessionLocal
from app.db.models import Bookmark

SCRENSHOT_DIRECTORY = "screenshots"
os.makedirs(SCRENSHOT_DIRECTORY, exist_ok=True)

celery_app = Celery(
    "Bookmark", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
)


def run(playwright: Playwright, url: str) -> str:
    url_hash = hashlib.sha3_256(url.encode()).hexdigest()
    screenshot_url = f"{os.path.join(SCRENSHOT_DIRECTORY, url_hash)}.png"

    try:
        with sync_playwright() as playwright:
            chromium = playwright.chromium
            browser = chromium.launch()
            page = browser.new_page()

            try:
                page.goto(url, timeout=60000)
            except PlaywrightTimeout:
                print(f"Timeout while loading {url}.")
                raise

            page.screenshot(path=screenshot_url, full_page=True, type="png")
            browser.close()

    except Exception as e:
        print(f"Error while taking a screenshot {e}.")
        raise
    return screenshot_url


@celery_app.task(
    autoretry_for=(PlaywrightTimeout,), retry_kwargs={"max retries": 3, "countdown": 10}
)
def screenshot(url: str, bookmark_id: int) -> None:
    screenshot_url = run(url)

    with SyncSessionLocal() as session:
        stmt = select(Bookmark).where(Bookmark.id == bookmark_id)
        result = session.execute(stmt)
        bookmark = result.scalar_one_or_none()
        if bookmark:
            bookmark.screenshot_url = screenshot_url
            session.commit()
            session.refresh(bookmark)
        else:
            print("Bookmark was deleted before worker finished the job.")


# TODO: Za pomocą alembica dodać kolumne "path" do tabeli bookmark - zawierającą URL do
# screenshotów(zmienna 'filename'). We funkcji screenshot połączyć się z bazą i dodać
# wszystko do odpowiedniego użytkownika pozdrwaiam
