import boto3
from celery import Celery
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
from sqlalchemy import select

from app.db.database import SyncSessionLocal
from app.db.models import Bookmark

celery_app = Celery(
    "Bookmark", broker="redis://redis:6379/0", backend="redis://redis:6379/1"
)

s3 = boto3.client("s3")
S3_BUCKET = "bookmark-screenshots"

def run(url: str, s3_key) -> str:
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()

            try:
                page = browser.new_page()
                page.goto(url, timeout=60000)
                screenshot = page.screenshot(full_page=True, type="png")
                
            except PlaywrightTimeout:
                            print(f"Timeout while loading {url}.")
                            raise
            
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=screenshot,
                ContentType="image/png"
                )
            browser.close()

    except Exception as e:
        print(f"Error while taking a screenshot {e}.")
        raise
    return s3_key


@celery_app.task(
    autoretry_for=(PlaywrightTimeout,), retry_kwargs={"max_retries": 3, "countdown": 10}
)
def page_screenshot(url: str, bookmark_id: int, s3_key: str):
    
    screenshot_url = run(url, s3_key)

    with SyncSessionLocal() as session:
        stmt = select(Bookmark).where(Bookmark.id == bookmark_id)
        result = session.execute(stmt)
        bookmark = result.scalar_one_or_none()
        if bookmark:
            bookmark.s3_key = screenshot_url
            session.commit()
            session.refresh(bookmark)
        else:
            print("Bookmark was deleted before worker finished the job.")