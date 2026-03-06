"""Search decision logic."""
import logging
from .schemas import Message

logger = logging.getLogger(__name__)

# Keywords that suggest web search is needed
SEARCH_KEYWORDS = {
    "latest", "current", "today", "recent", "search",
    "look up", "docs", "documentation", "release notes",
    "version", "pricing", "news", "find", "browse",
    "what is", "who is", "when", "where", "how to",
    "tutorial", "guide", "example", "api reference",
}


def needs_search(messages: list[Message]) -> bool:
    """
    Determine if web search is needed based on message content.
    
    Args:
        messages: List of chat messages
    
    Returns:
        True if search should be triggered
    """
    # Combine all user messages
    user_text = " ".join(
        msg.content.lower() 
        for msg in messages 
        if msg.role == "user"
    )
    
    # Check for search keywords
    has_keyword = any(keyword in user_text for keyword in SEARCH_KEYWORDS)
    
    if has_keyword:
        logger.info("Search triggered by keywords in: %s", user_text[:100])
    
    return has_keyword


def generate_queries(messages: list[Message], max_queries: int = 1) -> list[str]:
    """
    Generate search queries from conversation.
    
    Args:
        messages: List of chat messages
        max_queries: Maximum number of queries to generate
    
    Returns:
        List of search query strings
    """
    # Extract user messages
    user_messages = [msg.content for msg in messages if msg.role == "user"]
    
    if not user_messages:
        return []
    
    # Use the last user message as primary query
    last_message = user_messages[-1].strip()
    
    # For v1, just use the last user message as-is
    # Future: add query expansion, entity extraction, etc.
    queries = [last_message]
    
    logger.info("Generated %d search queries", len(queries))
    return queries[:max_queries]

