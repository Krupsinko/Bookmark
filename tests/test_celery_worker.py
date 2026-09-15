from unittest.mock import MagicMock, patch

import pytest

from worker import celery_worker

TEST_URL = "https://example.com"
TEST_S3_KEY = "user/1/test.png"
SCREENSHOT = b"png-content"


@pytest.fixture
def mock_worker_dependencies():
    with patch("worker.celery_worker.sync_playwright") as mock_sync_playwright:
        with patch("worker.celery_worker.s3") as mock_s3:
            playwright = MagicMock()
            chromium = MagicMock()
            browser = MagicMock()
            page = MagicMock()

            mock_sync_playwright.return_value.__enter__.return_value = playwright
            playwright.chromium = chromium
            chromium.launch.return_value = browser
            browser.new_page.return_value = page
            page.screenshot.return_value = SCREENSHOT

            yield chromium, browser, page, mock_s3


def test_page_screenshot_uploads_png_to_s3(mock_worker_dependencies):
    chromium, browser, page, mock_s3 = mock_worker_dependencies

    result = celery_worker.page_screenshot(TEST_URL, TEST_S3_KEY)

    chromium.launch.assert_called_once_with()
    browser.new_page.assert_called_once_with()
    page.goto.assert_called_once_with(TEST_URL, timeout=60000)
    page.screenshot.assert_called_once_with(full_page=True, type="png")
    mock_s3.put_object.assert_called_once_with(
        Bucket=celery_worker.s3_bucket_name,
        Key=TEST_S3_KEY,
        Body=SCREENSHOT,
        ContentType="image/png",
    )
    browser.close.assert_called_once_with()
    assert result == TEST_S3_KEY
