#!/usr/bin/env python3
"""
Example client demonstrating moonshot-local usage.
Shows both non-streaming and streaming requests.
"""
import os
import httpx
import json


API_URL = "http://127.0.0.1:8080"
API_KEY = os.getenv("MOONSHOT_LOCAL_API_KEY", "your-secret-key-here")


def test_models():
    """Test /v1/models endpoint."""
    print("=" * 60)
    print("Testing /v1/models")
    print("=" * 60)
    
    response = httpx.get(
        f"{API_URL}/v1/models",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_simple_chat():
    """Test simple chat completion (non-streaming)."""
    print("=" * 60)
    print("Testing simple chat (non-streaming)")
    print("=" * 60)
    
    response = httpx.post(
        f"{API_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "moonshot-local",
            "messages": [
                {"role": "user", "content": "Write a hello world in Python"}
            ],
            "stream": False,
        },
        timeout=30.0,
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    # Pretty print
    print(f"Model: {data['model']}")
    print(f"Content:\n{data['choices'][0]['message']['content']}")
    print()


def test_search_chat_streaming():
    """Test chat with search trigger (streaming)."""
    print("=" * 60)
    print("Testing chat with search (streaming)")
    print("This will trigger Firefox/Selenium search!")
    print("=" * 60)
    
    with httpx.stream(
        "POST",
        f"{API_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "moonshot-local",
            "messages": [
                {
                    "role": "user",
                    "content": "What are the latest features in Python 3.12? Give me a brief summary."
                }
            ],
            "stream": True,
        },
        timeout=60.0,
    ) as response:
        print(f"Status: {response.status_code}\n")
        print("Response:")
        
        for line in response.iter_lines():
            if not line:
                continue
            
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                
                if data_str == "[DONE]":
                    print("\n[DONE]")
                    break
                
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"]
                    
                    if "content" in delta:
                        print(delta["content"], end="", flush=True)
                    
                    if chunk["choices"][0].get("finish_reason"):
                        print(f"\n[finish_reason: {chunk['choices'][0]['finish_reason']}]")
                
                except json.JSONDecodeError:
                    continue
    
    print()


def main():
    """Run all tests."""
    print("\n🧪 Moonshot-Local Example Client\n")
    
    try:
        # Test 1: Models
        test_models()
        
        # Test 2: Simple chat
        test_simple_chat()
        
        # Test 3: Search-enabled streaming chat
        test_search_chat_streaming()
        
        print("✅ All tests completed successfully!")
        
    except httpx.ConnectError:
        print("❌ Could not connect to moonshot-local API")
        print("   Make sure the server is running: ./start.sh")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

