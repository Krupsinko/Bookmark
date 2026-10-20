import boto3
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, update, func
from sqlalchemy.orm import sessionmaker

from app.config import AwsSetting, DatabaseSettings
from app.enums import ScreenshotStatus
from app.db.models import Bookmark
from .celery_config import celery_app

aws_settings = AwsSetting()
db_settings = DatabaseSettings()

s3 = boto3.client("s3")
s3_bucket_name = aws_settings.S3_BUCKET_NAME


sync_db_url = db_settings.DATABASE_URL.set(drivername="postgresql+psycopg2")
sync_engine = create_engine(sync_db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=sync_engine)

def set_screenshot_status(bookmark_id: int, status: ScreenshotStatus) -> None:
    with SessionLocal() as session:
        session.execute(
            update(Bookmark).
            where(Bookmark.id==bookmark_id).
            values(
                screenshot_status=status,
                updated_at=func.now()
            )
        )
        session.commit()
    

@celery_app.task(
    bind=True,
    name="bookmark.page_screenshot",
    max_retries=3,
    default_retry_delay=10,
)
def page_screenshot(self, url: str, s3_key: str, bookmark_id: int) -> str:
    set_screenshot_status(bookmark_id, ScreenshotStatus.PROCESSING.value)

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, timeout=60000)
                screenshot = page.screenshot(full_page=True, type="png")

                s3.put_object(
                    Bucket=s3_bucket_name,
                    Key=s3_key,
                    Body=screenshot,
                    ContentType="image/png",
                )
            finally:
                browser.close()

    except PlaywrightTimeout as exc:
        if self.request.retries >= self.max_retries:
            set_screenshot_status(bookmark_id, ScreenshotStatus.FAILED.value)
            raise

        set_screenshot_status(bookmark_id, ScreenshotStatus.PENDING.value)
        raise self.retry(exc=exc)

    except Exception:
        set_screenshot_status(bookmark_id, ScreenshotStatus.FAILED.value)
        raise

    set_screenshot_status(bookmark_id, ScreenshotStatus.READY.value)
    return s3_key