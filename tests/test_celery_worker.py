import os
from unittest.mock import MagicMock, patch

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from celery_worker import page_screenshot, run

TEST_URL = "https://example.com"
TEST_BOOKMARK_ID = 1


@pytest.fixture
def mock_playwright_dependencies():
    with patch("celery_worker.sync_playwright") as mock_sync_playwright:
        
        # Playwright mocks
        mock_playwright_instance = MagicMock()
        mock_chromium = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()    
        
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_instance
        mock_playwright_instance.chromium = mock_chromium
        mock_chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        
        yield mock_chromium, mock_browser, mock_page
        
        
        
        
@pytest.fixture
def mock_database_dependencies():
    with patch("celery_worker.SyncSessionLocal") as mock_session_local:

        # Database objects mocks
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_bookmark = MagicMock()
    
        mock_session_local.return_value.__enter__.return_value = mock_session
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_bookmark
        
        yield mock_session, mock_result, mock_bookmark




def test_playwright(mock_playwright_dependencies):
    
    chromium, browser, page = mock_playwright_dependencies

    run(TEST_URL)

    chromium.launch.assert_called_once()
    page.goto.assert_called_once_with(TEST_URL, timeout=60000)
    page.screenshot.assert_called_once()
    browser.close.assert_called_once()



def test_page_screenshot(mock_database_dependencies):
    
    session, result, bookmark = mock_database_dependencies
    
    page_screenshot(TEST_URL, TEST_BOOKMARK_ID)


    session.execute.assert_called_once()
    result.scalar_one_or_none.assert_called_once()
    assert bookmark.screenshot_url is not None
    assert bookmark.screenshot_url.startswith("screenshots")
    assert bookmark.screenshot_url.endswith(".png")
    session.commit.assert_called_once()
    session.refresh.assert_called_with(bookmark)