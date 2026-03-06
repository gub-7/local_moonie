#!/usr/bin/env bash
# Quick start script for moonshot-local

set -e

echo "🚀 Starting moonshot-local proxy..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your settings, then run this script again."
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running at http://127.0.0.1:11434"
    echo "   Start it with: ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Check if geckodriver is available
if ! command -v geckodriver &> /dev/null; then
    echo "❌ geckodriver not found in PATH"
    echo "   Install with: sudo pacman -S geckodriver"
    exit 1
fi

echo "✅ geckodriver found"

# Check if Firefox is available
if ! command -v firefox &> /dev/null; then
    echo "❌ Firefox not found in PATH"
    echo "   Install with: sudo pacman -S firefox"
    exit 1
fi

echo "✅ Firefox found"
echo ""

# Start the server
echo "🌐 Starting server..."
python -m moonshot_local.app.main

