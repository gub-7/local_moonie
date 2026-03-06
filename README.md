# Moonshot-Local

Local OpenAI-compatible API proxy that combines Firefox/Selenium web search with Ollama LLM backend for Avante.nvim.

## Architecture

```
Avante.nvim
  ↓
moonshot-local API (FastAPI)
  ↓
Search Decision Engine
  ↓
Selenium + Firefox (Google search)
  ↓
Prompt Augmentation
  ↓
Ollama (llama3.2:3b)
  ↓
OpenAI-compatible SSE stream
```

## Features

- ✅ OpenAI-compatible `/v1/models` and `/v1/chat/completions` endpoints
- ✅ Streaming and non-streaming responses
- ✅ Automatic web search detection based on keywords
- ✅ Firefox/Selenium Google search scraping
- ✅ Search result injection into prompt context
- ✅ Ollama backend integration
- ✅ Graceful degradation if search fails
- ✅ Single-user stability with browser session management

## Prerequisites

### 1. Firefox and geckodriver

**Arch Linux:**
```bash
sudo pacman -S firefox geckodriver
```

**Other systems:**
- Install Firefox from https://www.mozilla.org/firefox/
- Download geckodriver from https://github.com/mozilla/geckodriver/releases
- Add geckodriver to PATH

### 2. Ollama

You already have Ollama running with:
```bash
OLLAMA_HOST=http://127.0.0.1:11434
ollama list
# NAME                        ID              SIZE
# llama3.2:3b                 a80c4f17acd5    2.0 GB
# mxbai-embed-large:latest    468836162de7    669 MB
```

### 3. Python 3.11+

```bash
python --version  # Should be 3.11 or higher
```

## Installation

```bash
# Clone/navigate to project
cd /home/gabe/tmpcode/local_moonie

# Install dependencies
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

## Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Ollama backend (already running on your system)
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=mxbai-embed-large:latest

# Server
HOST=127.0.0.1
PORT=8080
API_KEY=your-secret-key-here

# Search
MAX_SEARCH_RESULTS=5
SEARCH_TIMEOUT=10
HEADLESS_BROWSER=false  # Set to true to hide Firefox window
```

## Usage

### Start the server

```bash
python -m moonshot_local.app.main
```

Or with uvicorn:
```bash
uvicorn moonshot_local.app.main:app --host 127.0.0.1 --port 8080
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:moonshot_local.app.main:Starting moonshot-local proxy
INFO:moonshot_local.app.main:Ollama host: http://127.0.0.1:11434
INFO:moonshot_local.app.main:Ollama model: llama3.2:3b
INFO:moonshot_local.app.main:Listening on: 127.0.0.1:8080
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080
```

### Test with curl

**List models:**
```bash
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer your-secret-key-here"
```

**Chat completion (non-streaming):**
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [
      {"role": "user", "content": "Write a quicksort in Python"}
    ],
    "stream": false
  }'
```

**Chat with search (streaming):**
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [
      {"role": "user", "content": "What are the latest features in Avante.nvim?"}
    ],
    "stream": true
  }'
```

## Avante.nvim Configuration

Add to your Avante config (Lua):

```lua
return {
  provider = "moonshot_local",
  behaviour = {
    enable_fastapply = false,  -- Fast Apply requires separate Morph service
  },
  providers = {
    moonshot_local = {
      __inherited_from = "openai",
      endpoint = "http://127.0.0.1:8080/v1",
      api_key_name = "MOONSHOT_LOCAL_API_KEY",
      model = "moonshot-local",
    },
  },
}
```

Set environment variable:
```bash
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

## How It Works

### 1. Search Detection

Triggers on keywords like:
- `latest`, `current`, `today`, `recent`, `search`
- `docs`, `documentation`, `release notes`
- `version`, `pricing`, `news`
- `what is`, `how to`, `tutorial`

### 2. Search Flow

When search is triggered:
1. Extract query from last user message
2. Open Firefox via Selenium
3. Search Google
4. Scrape top N results (title, URL, snippet)
5. Inject into system prompt as structured context
6. Forward to Ollama
7. Stream response back to Avante

### 3. Graceful Degradation

If search fails:
- Log error
- Continue with original prompt
- Still return useful LLM response

## Project Structure

```
moonshot_local/
  app/
    main.py              # FastAPI routes
    schemas.py           # Pydantic models
    config.py            # Configuration
    browser.py           # Selenium browser manager
    search.py            # Google search scraper
    search_decider.py    # Search trigger logic
    prompting.py         # Prompt augmentation
    llm.py               # Ollama adapter
    sse.py               # SSE formatter
  __init__.py
pyproject.toml
.env.example
README.md
```

## Troubleshooting

### Firefox fails to start

**Error:** `selenium.common.exceptions.WebDriverException: Message: 'geckodriver' executable needs to be in PATH`

**Fix:**
```bash
# Arch Linux
sudo pacman -S geckodriver

# Or download manually
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
```

### Ollama connection refused

**Error:** `httpx.ConnectError: [Errno 111] Connection refused`

**Fix:**
```bash
# Start Ollama
ollama serve

# Verify it's running
curl http://127.0.0.1:11434/api/tags
```

### Search results empty

Check Firefox opens and navigates to Google. If you see CAPTCHA or consent pages, you may need to:
1. Run with `HEADLESS_BROWSER=false`
2. Manually accept consent once
3. Browser profile will persist for future runs

### Model too weak

`llama3.2:3b` works for testing but is weak for coding.

**Upgrade:**
```bash
# Pull a better model
ollama pull qwen2.5-coder:14b

# Update .env
OLLAMA_MODEL=qwen2.5-coder:14b

# Restart server
```

## Limitations

- **v1 scope:** Single-user, serialized browser access
- **Search fragility:** Google DOM changes can break scraping
- **No Fast Apply:** Avante Fast Apply requires separate Morph service
- **Model quality:** llama3.2:3b is small; upgrade for production use

## Roadmap

Future improvements:
- [ ] Add result caching
- [ ] Support multiple search providers (DuckDuckGo, Brave API)
- [ ] Add page content extraction after SERP
- [ ] Add local reranker
- [ ] Pool multiple browser instances
- [ ] Tool-call emulation for Moonshot-like behavior
- [ ] Optional Morph-compatible apply service

## License

MIT

## Credits

Built for Avante.nvim local setup with Ollama + Firefox search.

