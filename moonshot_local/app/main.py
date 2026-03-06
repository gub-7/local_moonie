"""FastAPI application - moonshot-local proxy."""
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import config
from .schemas import (
    ChatRequest,
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionMessage,
    Usage,
)
from .search_decider import needs_search, generate_queries
from .search import search_multiple_queries
from .prompting import augment_with_search_results
from .llm import ollama_chat_stream, ollama_chat_complete
from .sse import create_chunk, format_sse_line, format_done
from .browser import close_driver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting moonshot-local proxy")

    # Display env file path
    env_file_path = config.get_env_file_path()
    if env_file_path:
        logger.info("Configuration loaded from: %s", env_file_path)
    else:
        logger.info("Configuration loaded from: environment variables only (no .env file found)")

    logger.info("Ollama host: %s", config.OLLAMA_HOST)
    logger.info("Ollama model: %s", config.OLLAMA_MODEL)
    logger.info("Listening on: %s:%s", config.HOST, config.PORT)
    yield
    logger.info("Shutting down moonshot-local proxy")
    close_driver()


app = FastAPI(
    title="Moonshot-Local",
    description="Local OpenAI-compatible proxy with Firefox/Selenium search + Ollama backend for Avante.nvim by @yetone (https://github.com/yetone/avante.nvim)",
    version="0.1.0",
    lifespan=lifespan,
)


def verify_api_key(credentials: HTTPAuthorizationCredentials | None = Security(security)):
    """Verify API key if configured."""
    if not config.API_KEY:
        # No API key required
        return
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    if credentials.credentials != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@app.get("/v1/models")
async def list_models(_: None = Security(verify_api_key)):
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": config.EXPOSED_MODEL,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "self-hosted",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    _: None = Security(verify_api_key),
):
    """
    OpenAI-compatible chat completions endpoint.
    
    Supports both streaming and non-streaming responses.
    Optionally performs web search and augments prompt.
    """
    logger.info(
        "Chat request: model=%s, messages=%d, stream=%s",
        request.model,
        len(request.messages),
        request.stream,
    )
    
    # Decide if search is needed
    should_search = needs_search(request.messages)
    search_results = []
    
    if should_search:
        try:
            logger.info("Search triggered")
            queries = generate_queries(request.messages, max_queries=1)
            
            if queries:
                search_results = search_multiple_queries(
                    queries,
                    limit_per_query=config.MAX_SEARCH_RESULTS,
                )
                logger.info("Retrieved %d search results", len(search_results))
        except Exception as e:
            logger.error("Search failed: %s", e)
            # Continue without search results
    
    # Augment prompt with search results
    augmented_messages = augment_with_search_results(request.messages, search_results)
    
    # Handle non-streaming response
    if not request.stream:
        try:
            content = await ollama_chat_complete(augmented_messages)
            
            return ChatCompletion(
                id=f"chatcmpl-{int(time.time())}",
                created=int(time.time()),
                model=config.EXPOSED_MODEL,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=ChatCompletionMessage(
                            role="assistant",
                            content=content,
                        ),
                        finish_reason="stop",
                    )
                ],
                usage=Usage(),
            )
        except Exception as e:
            logger.error("LLM error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LLM backend error: {str(e)}",
            )
    
    # Handle streaming response
    async def stream_generator() -> AsyncIterator[bytes]:
        """Generate SSE stream."""
        chunk_id = f"chatcmpl-{int(time.time())}"
        
        try:
            # Send initial chunk with role
            initial_chunk = create_chunk(
                role="assistant",
                model=config.EXPOSED_MODEL,
                chunk_id=chunk_id,
            )
            yield format_sse_line(initial_chunk)
            
            # Stream from Ollama
            async for obj in ollama_chat_stream(augmented_messages):
                token = obj.get("message", {}).get("content")
                done = obj.get("done", False)
                
                if token:
                    chunk = create_chunk(
                        content=token,
                        model=config.EXPOSED_MODEL,
                        chunk_id=chunk_id,
                    )
                    yield format_sse_line(chunk)
                
                if done:
                    # Send final chunk with finish_reason
                    final_chunk = create_chunk(
                        finish_reason="stop",
                        model=config.EXPOSED_MODEL,
                        chunk_id=chunk_id,
                    )
                    yield format_sse_line(final_chunk)
                    break
            
            # Send [DONE] marker
            yield format_done()
            
        except Exception as e:
            logger.error("Streaming error: %s", e)
            # Send error chunk
            error_chunk = create_chunk(
                content=f"\n\n[Error: {str(e)}]",
                finish_reason="error",
                model=config.EXPOSED_MODEL,
                chunk_id=chunk_id,
            )
            yield format_sse_line(error_chunk)
            yield format_done()
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


def main():
    """CLI entry point for moonshot-local."""
    import uvicorn

    uvicorn.run(
        "moonshot_local.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()

