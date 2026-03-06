"""Ollama LLM adapter."""
import json
import logging
import httpx
from typing import AsyncIterator

from .config import config

logger = logging.getLogger(__name__)


async def ollama_chat_stream(messages: list[dict]) -> AsyncIterator[dict]:
    """
    Call Ollama chat API in streaming mode.
    
    Args:
        messages: List of message dicts
    
    Yields:
        Parsed JSON objects from Ollama stream
    """
    url = f"{config.OLLAMA_HOST}/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
    }
    
    logger.info("Calling Ollama at %s with model %s", url, config.OLLAMA_MODEL)
    
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if not line:
                    continue
                
                try:
                    obj = json.loads(line)
                    yield obj
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse Ollama response line: %s", e)
                    continue


async def ollama_chat_complete(messages: list[dict]) -> str:
    """
    Call Ollama chat API in non-streaming mode.
    
    Args:
        messages: List of message dicts
    
    Returns:
        Complete response content string
    """
    url = f"{config.OLLAMA_HOST}/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    
    logger.info("Calling Ollama at %s with model %s (non-streaming)", url, config.OLLAMA_MODEL)
    
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        content = data.get("message", {}).get("content", "")
        return content

