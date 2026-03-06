"""Pydantic schemas for OpenAI-compatible API."""
from typing import Literal
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = "moonshot-local"
    messages: list[Message]
    stream: bool = True
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None


class ChatCompletionMessage(BaseModel):
    """Chat completion message."""
    role: str
    content: str


class ChatCompletionChoice(BaseModel):
    """Chat completion choice."""
    index: int
    message: ChatCompletionMessage
    finish_reason: str | None = None


class Usage(BaseModel):
    """Token usage stats."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletion(BaseModel):
    """Non-streaming chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Usage = Usage()


class DeltaMessage(BaseModel):
    """Streaming delta message."""
    role: str | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    """Streaming chunk choice."""
    index: int
    delta: DeltaMessage
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    """Streaming chat completion chunk."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice]


class SearchResult(BaseModel):
    """Single search result."""
    rank: int
    title: str
    url: str
    snippet: str = ""


class SearchBundle(BaseModel):
    """Search results bundle."""
    queries: list[str]
    results: list[SearchResult]
    search_status: Literal["ok", "failed", "skipped"]
    error: str | None = None

