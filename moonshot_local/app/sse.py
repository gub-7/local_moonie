"""SSE (Server-Sent Events) streaming formatter for OpenAI compatibility."""
import json
import time
import uuid
from .schemas import ChatCompletionChunk, ChatCompletionChunkChoice, DeltaMessage


def create_chunk(
    content: str | None = None,
    finish_reason: str | None = None,
    role: str | None = None,
    model: str = "moonshot-local",
    chunk_id: str | None = None,
) -> ChatCompletionChunk:
    """
    Create an OpenAI-compatible streaming chunk.
    
    Args:
        content: Text content delta
        finish_reason: Reason for completion end (e.g., "stop")
        role: Message role (only for first chunk)
        model: Model name
        chunk_id: Unique chunk ID (generated if None)
    
    Returns:
        ChatCompletionChunk object
    """
    if chunk_id is None:
        chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    
    delta = DeltaMessage(role=role, content=content)
    choice = ChatCompletionChunkChoice(
        index=0,
        delta=delta,
        finish_reason=finish_reason,
    )
    
    return ChatCompletionChunk(
        id=chunk_id,
        created=int(time.time()),
        model=model,
        choices=[choice],
    )


def format_sse_line(chunk: ChatCompletionChunk) -> bytes:
    """
    Format a chunk as an SSE line.
    
    Args:
        chunk: ChatCompletionChunk to format
    
    Returns:
        Formatted SSE line as bytes
    """
    json_str = chunk.model_dump_json(exclude_none=True)
    return f"data: {json_str}\n\n".encode("utf-8")


def format_done() -> bytes:
    """Format the final [DONE] SSE marker."""
    return b"data: [DONE]\n\n"

