# Moonshot-Local

Local OpenAI-compatible API proxy that combines Firefox/Selenium web search with Ollama LLM backend for [Avante](https://github.com/yetone/avante.nvim) by [@yetone](https://github.com/yetone).

## What is this?

A local service that gives [Avante.nvim](https://github.com/yetone/avante.nvim) web search capabilities while keeping everything private and self-hosted. It replicates Moonshot/Kimi's built-in web search feature using:
- **Firefox + Selenium** for Google search
- **Ollama** for local LLM generation
- **FastAPI** for OpenAI-compatible endpoints

## Architecture

```
Avante.nvim (by yetone)
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

## Quick Start

### 1. Install System Dependencies

**Arch Linux:**
```bash
sudo pacman -S firefox geckodriver python python-pip
```

**Other systems:**
- Firefox: https://www.mozilla.org/firefox/
- geckodriver: https://github.com/mozilla/geckodriver/releases
- Python 3.11+

### 2. Verify Ollama

```bash
# Check Ollama is running
curl http://127.0.0.1:11434/api/tags

# Should show your models (e.g., llama3.2:3b)
```

If not running:
```bash
ollama serve
```

### 3. Install moonshot-local

**Option A: Install from PyPI (recommended):**
```bash
pip install moonshot-local
```

**Option B: Install from source:**
```bash
git clone https://github.com/yourusername/moonshot-local.git
cd moonshot-local
pip install -e .
```

### 4. Configure

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

**Important settings in .env:**
```bash
# Ollama backend (adjust to your setup)
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b

# Set a secure API key
API_KEY=your-secret-key-here

# Browser visibility
HEADLESS_BROWSER=false  # false = visible, true = headless
```

### 5. Start Server

**Quick start:**
```bash
./start.sh
```

**Or manually:**
```bash
python -m moonshot_local.app.main
```

**Or with uvicorn:**
```bash
uvicorn moonshot_local.app.main:app --host 127.0.0.1 --port 8080
```

### 6. Test

```bash
# Set API key
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here

# Run tests
./test_api.sh

# Or use Python example
python example_client.py
```

## Avante.nvim Integration

[Avante.nvim](https://github.com/yetone/avante.nvim) by [@yetone](https://github.com/yetone) is a Neovim plugin that brings Cursor-like AI features to Neovim.

### Configure Avante

Add to your Neovim config (e.g., `~/.config/nvim/lua/plugins/avante.lua`):

```lua
return {
  "yetone/avante.nvim",
  event = "VeryLazy",
  opts = {
    -- Use moonshot_local as provider
    provider = "moonshot_local",

    behaviour = {
      -- Fast Apply requires separate Morph service
      enable_fastapply = false,
    },

    providers = {
      moonshot_local = {
        -- Inherit OpenAI-compatible behavior
        __inherited_from = "openai",

        -- Point to local proxy
        endpoint = "http://127.0.0.1:8080/v1",

        -- API key from environment
        api_key_name = "MOONSHOT_LOCAL_API_KEY",

        -- Model name
        model = "moonshot-local",

        -- Optional settings
        temperature = 0.2,
        max_tokens = 4096,
      },
    },
  },

  dependencies = {
    "stevearc/dressing.nvim",
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    "nvim-tree/nvim-web-devicons",
  },
}
```

### Set API Key

```bash
# Add to your shell rc file (~/.bashrc, ~/.zshrc, etc.)
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here

# Or set for current session
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

### Use in Avante

1. Start moonshot-local: `./start.sh`
2. Open Neovim
3. Use [Avante](https://github.com/yetone/avante.nvim) commands as normal

**Search triggers when you ask about:**
- "latest", "current", "recent" info
- Documentation, release notes
- "How to" questions
- Version-specific queries

## How It Works

### Normal Coding Prompt

```
User in Avante: "Write quicksort in Python"
  ↓
moonshot-local: No search keywords detected
  ↓
Ollama (llama3.2:3b): Generate code
  ↓
Stream back to Avante
```

### Search-Enabled Prompt

```
User in Avante: "What are the latest features in FastAPI?"
  ↓
moonshot-local: Detected "latest" keyword
  ↓
Firefox + Selenium: Search Google
  ↓
Scrape top 5 results (title, URL, snippet)
  ↓
Inject into prompt:
  "WEB_RESULTS:
   [1] FastAPI 0.109.0 Release
   URL: https://...
   Snippet: New features include..."
  ↓
Ollama: Generate answer with web context
  ↓
Stream back to Avante with citations
```

### Search Trigger Keywords

Search activates when prompt contains:
- `latest`, `current`, `today`, `recent`, `search`
- `docs`, `documentation`, `release notes`
- `version`, `pricing`, `news`
- `what is`, `how to`, `tutorial`

## API Endpoints

### GET /v1/models
Returns available models (OpenAI-compatible).

```bash
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer your-secret-key-here"
```

### POST /v1/chat/completions
Main endpoint for chat completions.

**Request:**
```json
{
  "model": "moonshot-local",
  "messages": [
    {"role": "user", "content": "Your prompt here"}
  ],
  "stream": true,
  "temperature": 0.2
}
```

**Non-streaming example:**
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

**Streaming example:**
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [{"role": "user", "content": "latest Python features"}],
    "stream": true
  }'
```

### GET /health
Health check endpoint.

```bash
curl http://127.0.0.1:8080/health
```

## Configuration Reference

All settings in `.env`:

```bash
# Ollama backend
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
HEADLESS_BROWSER=false
```

## Project Structure

```
moonshot_local/
├── app/
│   ├── main.py              # FastAPI routes
│   ├── schemas.py           # Pydantic models (OpenAI-compatible)
│   ├── config.py            # Configuration from .env
│   ├── browser.py           # Selenium Firefox manager
│   ├── search.py            # Google search scraper
│   ├── search_decider.py    # Search trigger logic
│   ├── prompting.py         # Prompt augmentation
│   ├── llm.py               # Ollama adapter
│   └── sse.py               # SSE streaming formatter
└── __init__.py

pyproject.toml               # Dependencies
.env.example                 # Configuration template
README.md                    # This file
start.sh                     # Quick start script
test_api.sh                  # Test script
example_client.py            # Python example client
avante_config.lua            # Avante config example
moonshot-local.service       # systemd service file
```

## Upgrading the Model

`llama3.2:3b` is fast but weak for complex coding. Upgrade for better quality:

```bash
# Pull a better model
ollama pull qwen2.5-coder:14b

# Or for 32B if you have VRAM
ollama pull qwen2.5-coder:32b

# Update .env
nano .env
# Change: OLLAMA_MODEL=qwen2.5-coder:14b

# Restart server
```

**Model recommendations:**
- `qwen2.5-coder:14b` - Great for coding (~8GB VRAM)
- `qwen2.5-coder:32b` - Best for coding (~20GB VRAM)
- `deepseek-coder-v2:16b` - Alternative for code
- `llama3.3:70b` - If you have 48GB+ VRAM

## Troubleshooting

### Server won't start

**Error: `Address already in use`**
```bash
# Check what's using port 8080
sudo lsof -i :8080

# Kill it or change PORT in .env
```

**Error: `ModuleNotFoundError`**
```bash
# Reinstall
pip install -e .
```

### Ollama connection fails

**Error: `Connection refused`**
```bash
# Start Ollama
ollama serve

# Verify
curl http://127.0.0.1:11434/api/tags
```

### Firefox/geckodriver issues

**Error: `geckodriver not found`**
```bash
# Arch Linux
sudo pacman -S geckodriver

# Verify
geckodriver --version
```

**Firefox opens but search fails:**
1. Set `HEADLESS_BROWSER=false` in .env
2. Watch Firefox window
3. If Google consent page appears, accept it manually once
4. Profile persists, won't ask again

**Search returns no results:**
- Google may have changed DOM structure
- Check logs for scraping errors
- System still works - degrades gracefully to LLM without web context

### Avante integration issues

**Avante can't connect:**
```bash
# Verify server is running
curl http://127.0.0.1:8080/health

# Check API key matches
echo $MOONSHOT_LOCAL_API_KEY

# In Neovim, check env var is visible:
:lua print(vim.fn.getenv('MOONSHOT_LOCAL_API_KEY'))
```

**Streaming doesn't work:**
- Ensure [Avante](https://github.com/yetone/avante.nvim) provider inherits from "openai"
- Check `stream = true` is supported in your Avante version

## Running as systemd Service

```bash
# Copy service file
sudo cp moonshot-local.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/moonshot-local.service

# Enable and start
sudo systemctl enable moonshot-local
sudo systemctl start moonshot-local

# Check status
sudo systemctl status moonshot-local

# View logs
sudo journalctl -u moonshot-local -f
```

## Advanced Usage

### Custom Search Keywords

Edit `moonshot_local/app/search_decider.py`:

```python
SEARCH_KEYWORDS = {
    "latest", "current", "today", "recent", "search",
    "your", "custom", "keywords", "here",
}
```

### Multiple Search Queries

Edit `moonshot_local/app/search_decider.py`:

```python
def generate_queries(messages: list[Message], max_queries: int = 3):  # Changed from 1
    # Add query expansion logic
```

### Adjust Search Results

In `.env`:
```bash
MAX_SEARCH_RESULTS=10  # Default is 5
SEARCH_TIMEOUT=15      # Default is 10
```

## Performance

- **Normal prompts:** ~Same as direct Ollama
- **Search prompts:** +2-5 seconds for Firefox/scraping
- **Model quality:** Depends on your Ollama model

## Limitations

- **v1 scope:** Single-user, serialized browser access
- **Search fragility:** Google DOM changes can break scraping
- **No Fast Apply:** [Avante](https://github.com/yetone/avante.nvim) Fast Apply requires separate Morph service
- **Model quality:** Depends on your Ollama model choice

## Roadmap

Future improvements:
- [ ] Result caching (Redis/SQLite)
- [ ] Multiple search providers (DuckDuckGo, Brave API)
- [ ] Full page content extraction
- [ ] Local reranker for results
- [ ] Multi-browser pool
- [ ] Tool-call emulation for Moonshot-like behavior
- [ ] Morph-compatible Fast Apply service
- [ ] Embeddings endpoint for RAG

## Security Notes

- API key required by default (set in .env)
- Binds to localhost by default (not exposed to network)
- For production: use HTTPS reverse proxy, stronger auth

## Credits

Built for [Avante.nvim](https://github.com/yetone/avante.nvim) by [@yetone](https://github.com/yetone) with:
- FastAPI (web framework)
- Selenium (browser automation)
- Ollama (local LLM)
- Firefox (web search)

## License

MIT

