"""Selenium browser manager."""
import threading
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from .config import config

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_driver = None
_query_count = 0
_max_queries_before_restart = 100


def get_driver():
    """Get or create singleton Firefox WebDriver."""
    global _driver, _query_count
    
    with _lock:
        if _driver is None or _query_count >= _max_queries_before_restart:
            if _driver is not None:
                try:
                    _driver.quit()
                    logger.info("Restarted browser after %d queries", _query_count)
                except Exception as e:
                    logger.warning("Error quitting old driver: %s", e)
            
            opts = Options()
            if config.HEADLESS_BROWSER:
                opts.add_argument("-headless")
            
            try:
                _driver = webdriver.Firefox(options=opts)
                _query_count = 0
                logger.info("Firefox browser started (headless=%s)", config.HEADLESS_BROWSER)
            except Exception as e:
                logger.error("Failed to start Firefox: %s", e)
                raise
        
        return _driver


def increment_query_count():
    """Increment query counter for browser restart logic."""
    global _query_count
    with _lock:
        _query_count += 1


def close_driver():
    """Close the browser."""
    global _driver
    with _lock:
        if _driver is not None:
            try:
                _driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning("Error closing browser: %s", e)
            finally:
                _driver = None

