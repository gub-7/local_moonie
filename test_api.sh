#!/usr/bin/env bash
# Test script for moonshot-local

API_URL="http://127.0.0.1:8080"
API_KEY="${MOONSHOT_LOCAL_API_KEY:-your-secret-key-here}"

echo "🧪 Testing moonshot-local API"
echo ""

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
curl -s "$API_URL/health" | jq .
echo ""

# Test 2: List models
echo "2️⃣  Testing /v1/models..."
curl -s "$API_URL/v1/models" \
  -H "Authorization: Bearer $API_KEY" | jq .
echo ""

# Test 3: Simple chat (non-streaming)
echo "3️⃣  Testing simple chat completion (non-streaming)..."
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "moonshot-local",
    "messages": [
      {"role": "user", "content": "Say hello in one sentence"}
    ],
    "stream": false
  }' | jq .
echo ""

# Test 4: Chat with search trigger (streaming)
echo "4️⃣  Testing chat with search trigger (streaming)..."
echo "   (This will open Firefox and search Google)"
curl -s "$API_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "moonshot-local",
    "messages": [
      {"role": "user", "content": "What are the latest features in Python 3.12?"}
    ],
    "stream": true
  }'
echo ""
echo ""

echo "✅ Tests complete"

