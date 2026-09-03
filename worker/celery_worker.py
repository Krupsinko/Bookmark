import boto3
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

from app.config import AwsSetting

from .celery_config import celery_app

aws_settings = AwsSetting()

s3 = boto3.client("s3")
s3_bucket_name = aws_settings.S3_BUCKET_NAME


@celery_app.task(
    name="bookmark.page_screenshot",
    autoretry_for=(PlaywrightTimeout,), 
    retry_kwargs={"max_retries": 3, "countdown": 10}
)
def page_screenshot(url: str, s3_key) -> str:
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
                Bucket=s3_bucket_name,
                Key=s3_key,
                Body=screenshot,
                ContentType="image/png"
                )
            browser.close()

    except Exception as e:
        print(f"Error while taking a screenshot {e}.")
        raise
    return s3_key
