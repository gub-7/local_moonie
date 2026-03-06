"""Google search scraper using Selenium."""
import logging
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .browser import get_driver, increment_query_count
from .config import config
from .schemas import SearchResult

logger = logging.getLogger(__name__)


def google_search(query: str, limit: int | None = None) -> list[SearchResult]:
    """
    Perform Google search and scrape organic results.
    
    Args:
        query: Search query string
        limit: Maximum number of results (defaults to config.MAX_SEARCH_RESULTS)
    
    Returns:
        List of SearchResult objects
    """
    if limit is None:
        limit = config.MAX_SEARCH_RESULTS
    
    results = []
    
    try:
        driver = get_driver()
        increment_query_count()
        
        # Navigate to Google search
        search_url = f"https://www.google.com/search?q={quote(query)}"
        logger.info("Searching Google: %s", query)
        driver.get(search_url)
        
        # Wait for results to load
        try:
            WebDriverWait(driver, config.SEARCH_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a h3"))
            )
        except TimeoutException:
            logger.warning("Timeout waiting for search results for query: %s", query)
            return results
        
        # Find all result headings
        seen_urls = set()
        h3_elements = driver.find_elements(By.CSS_SELECTOR, "a h3")
        
        for rank, h3 in enumerate(h3_elements, start=1):
            if len(results) >= limit:
                break
            
            try:
                # Get parent anchor element
                anchor = h3.find_element(By.XPATH, "./ancestor::a[1]")
                url = anchor.get_attribute("href")
                title = h3.text.strip()
                
                # Skip invalid or duplicate results
                if not url or not title or url in seen_urls:
                    continue
                
                # Try to extract snippet
                snippet = ""
                try:
                    # Look for snippet in parent div
                    parent_div = anchor.find_element(By.XPATH, "./ancestor::div[1]")
                    snippet_text = parent_div.text.strip()
                    
                    # Remove title from snippet if present
                    if snippet_text.startswith(title):
                        snippet = snippet_text[len(title):].strip()
                    else:
                        snippet = snippet_text
                    
                    # Limit snippet length
                    if len(snippet) > 500:
                        snippet = snippet[:497] + "..."
                        
                except Exception:
                    # Snippet extraction is best-effort
                    pass
                
                results.append(SearchResult(
                    rank=len(results) + 1,
                    title=title,
                    url=url,
                    snippet=snippet
                ))
                seen_urls.add(url)
                
            except Exception as e:
                logger.debug("Error extracting result %d: %s", rank, e)
                continue
        
        logger.info("Found %d results for query: %s", len(results), query)
        
    except WebDriverException as e:
        logger.error("WebDriver error during search: %s", e)
    except Exception as e:
        logger.error("Unexpected error during search: %s", e)
    
    return results


def search_multiple_queries(queries: list[str], limit_per_query: int | None = None) -> list[SearchResult]:
    """
    Execute multiple search queries and combine results.
    
    Args:
        queries: List of search query strings
        limit_per_query: Max results per query
    
    Returns:
        Combined list of SearchResult objects with updated ranks
    """
    all_results = []
    seen_urls = set()
    
    for query in queries:
        query_results = google_search(query, limit=limit_per_query)
        
        # Deduplicate across queries
        for result in query_results:
            if result.url not in seen_urls:
                all_results.append(result)
                seen_urls.add(result.url)
    
    # Re-rank combined results
    for idx, result in enumerate(all_results, start=1):
        result.rank = idx
    
    return all_results

