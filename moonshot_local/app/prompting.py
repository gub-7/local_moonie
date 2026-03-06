"""Prompt augmentation with search results."""
import logging
from .schemas import Message, SearchResult

logger = logging.getLogger(__name__)


def augment_with_search_results(messages: list[Message], results: list[SearchResult]) -> list[dict]:
    """
    Inject search results into message context.
    
    Args:
        messages: Original chat messages
        results: Search results to inject
    
    Returns:
        Augmented messages as dicts for Ollama
    """
    if not results:
        # No search results, return original messages
        return [msg.model_dump() for msg in messages]
    
    # Build web results block
    web_block_lines = []
    for result in results:
        web_block_lines.append(f"[{result.rank}] {result.title}")
        web_block_lines.append(f"URL: {result.url}")
        if result.snippet:
            web_block_lines.append(f"Snippet: {result.snippet}")
        web_block_lines.append("")  # Blank line between results
    
    web_block = "\n".join(web_block_lines)
    
    # Create system message with web context
    system_content = (
        "You are a helpful coding and research assistant. "
        "The following WEB_RESULTS have been retrieved to help answer the user's question. "
        "Use them as supporting context when relevant. "
        "Cite sources by title when you reference specific information.\n\n"
        f"WEB_RESULTS:\n{web_block}\n"
    )
    
    system_message = {"role": "system", "content": system_content}
    
    # Convert original messages to dicts
    original_messages = [msg.model_dump() for msg in messages]
    
    # Check if there's already a system message
    has_system = any(msg.get("role") == "system" for msg in original_messages)
    
    if has_system:
        # Prepend web context to existing system message
        for msg in original_messages:
            if msg.get("role") == "system":
                msg["content"] = system_content + "\n" + msg["content"]
                break
        augmented = original_messages
    else:
        # Add new system message at the start
        augmented = [system_message] + original_messages
    
    logger.info("Augmented prompt with %d search results", len(results))
    return augmented

