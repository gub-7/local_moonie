# Installation & Usage Guide

## Complete Installation Steps

### 1. System Dependencies

```bash
# Arch Linux (your system)
sudo pacman -S firefox geckodriver python python-pip

# Verify installations
firefox --version
geckodriver --version
python --version  # Should be 3.11+
```

### 2. Verify Ollama

You already have Ollama running. Verify:

```bash
# Check Ollama is running
curl http://127.0.0.1:11434/api/tags

# Should show your models:
# - llama3.2:3b
# - mxbai-embed-large:latest
```

### 3. Install moonshot-local

```bash
cd /home/gabe/tmpcode/local_moonie

# Install in development mode
pip install -e .

# Or with dev dependencies for testing
pip install -e ".[dev]"
```

### 4. Configure

```bash
# Create .env from example
cp .env.example .env

# Edit configuration
nano .env
```

**Important settings in .env:**
```bash
# These match your existing Ollama setup
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b

# Set a secure API key
API_KEY=your-secret-key-here

# Browser visibility (false = visible, true = headless)
HEADLESS_BROWSER=false
```

### 5. Set Environment Variable

```bash
# Add to your ~/.bashrc or ~/.zshrc
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here

# Or set for current session
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

## Running the Server

### Option 1: Quick Start Script

```bash
./start.sh
```

This will:
- Check all dependencies
- Verify Ollama is running
- Start the server

### Option 2: Manual Start

```bash
python -m moonshot_local.app.main
```

### Option 3: With uvicorn

```bash
uvicorn moonshot_local.app.main:app --host 127.0.0.1 --port 8080
```

### Option 4: As systemd service

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

## Testing

### Quick Test

```bash
# Make sure API key is set
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here

# Run test script
./test_api.sh
```

### Python Example Client

```bash
python example_client.py
```

This will:
1. Test `/v1/models`
2. Test simple chat (no search)
3. Test search-enabled chat (opens Firefox)

### Manual curl Tests

**Health check:**
```bash
curl http://127.0.0.1:8080/health
```

**List models:**
```bash
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer your-secret-key-here"
```

**Simple chat:**
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

**Search-enabled chat:**
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

## Avante.nvim Integration

### 1. Configure Avante

Add to your Neovim config (e.g., `~/.config/nvim/lua/plugins/avante.lua`):

```lua
return {
  "yetone/avante.nvim",
  event = "VeryLazy",
  opts = {
    provider = "moonshot_local",
    
    behaviour = {
      enable_fastapply = false,  -- Requires separate Morph service
    },
    
    providers = {
      moonshot_local = {
        __inherited_from = "openai",
        endpoint = "http://127.0.0.1:8080/v1",
        api_key_name = "MOONSHOT_LOCAL_API_KEY",
        model = "moonshot-local",
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

### 2. Set API Key

Make sure the API key is available to Neovim:

```bash
# Add to your shell rc file
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

### 3. Use in Neovim

1. Start moonshot-local server: `./start.sh`
2. Open Neovim
3. Use Avante commands as normal

**Search will trigger when you ask about:**
- "latest", "current", "recent" info
- Documentation, release notes
- "How to" questions
- Version-specific queries

## Usage Examples

### Example 1: Simple Coding Task

**Prompt in Avante:**
```
Write a quicksort function in Python
```

**Behavior:**
- No search triggered
- Goes directly to llama3.2:3b
- Returns code

### Example 2: Documentation Query

**Prompt in Avante:**
```
What are the latest features in FastAPI?
```

**Behavior:**
1. Detects "latest" keyword
2. Opens Firefox
3. Searches Google for "What are the latest features in FastAPI?"
4. Scrapes top 5 results
5. Injects results into prompt as context
6. Sends augmented prompt to llama3.2:3b
7. Streams response citing sources

### Example 3: Mixed Query

**Prompt in Avante:**
```
Show me how to use the new Python 3.12 type hints with examples
```

**Behavior:**
1. Detects "new" + "Python 3.12"
2. Searches for Python 3.12 type hints docs
3. Augments prompt with search results
4. Generates code examples using llama3.2:3b with web context

## Upgrading the Model

llama3.2:3b works but is weak for complex coding. To upgrade:

```bash
# Pull a better model
ollama pull qwen2.5-coder:14b

# Or for 32B if you have VRAM
ollama pull qwen2.5-coder:32b

# Update .env
nano .env
# Change: OLLAMA_MODEL=qwen2.5-coder:14b

# Restart server
# Ctrl+C to stop, then ./start.sh
```

**Model recommendations:**
- `qwen2.5-coder:14b` - Great for coding, 14B params (~8GB VRAM)
- `qwen2.5-coder:32b` - Best for coding, 32B params (~20GB VRAM)
- `deepseek-coder-v2:16b` - Alternative, good for code
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
# Install
sudo pacman -S geckodriver

# Verify
geckodriver --version
```

**Firefox opens but search fails**
1. Set `HEADLESS_BROWSER=false` in .env
2. Watch Firefox window
3. If you see Google consent page, accept it manually once
4. Profile persists, won't ask again

**Search returns no results**
- Google may have changed DOM structure
- Check logs for scraping errors
- Search still degrades gracefully - LLM answers without web context

### Avante integration issues

**Avante can't connect**
```bash
# Verify server is running
curl http://127.0.0.1:8080/health

# Check API key matches
echo $MOONSHOT_LOCAL_API_KEY

# Check Neovim can see env var
# In Neovim:
:lua print(vim.fn.getenv('MOONSHOT_LOCAL_API_KEY'))
```

**Streaming doesn't work**
- Make sure Avante provider inherits from "openai"
- Check `stream = true` is supported in your Avante version

### Performance issues

**Slow responses**
- llama3.2:3b is small but fast
- Upgrade model if quality is poor
- Search adds 2-5 seconds overhead

**Browser crashes**
- Increase `_max_queries_before_restart` in `browser.py`
- Or set `HEADLESS_BROWSER=true` for stability

## Advanced Configuration

### Multiple Search Queries

Edit `moonshot_local/app/search_decider.py`:

```python
def generate_queries(messages: list[Message], max_queries: int = 3):  # Changed from 1
    # Add query expansion logic
```

### Custom Search Keywords

Edit `moonshot_local/app/search_decider.py`:

```python
SEARCH_KEYWORDS = {
    "latest", "current", "today", "recent", "search",
    "your", "custom", "keywords", "here",
}
```

### Change Search Results Limit

In `.env`:
```bash
MAX_SEARCH_RESULTS=10  # Default is 5
```

### Headless Mode

In `.env`:
```bash
HEADLESS_BROWSER=true  # Hides Firefox window
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when you write them)
pytest
```

### Code Formatting

```bash
# Format with ruff
ruff check moonshot_local/
ruff format moonshot_local/
```

### Logs

Server logs to stdout. For systemd service:
```bash
sudo journalctl -u moonshot-local -f
```

## Architecture Recap

```
┌─────────────┐
│ Avante.nvim │
└──────┬──────┘
       │ HTTP POST /v1/chat/completions
       │
┌──────▼──────────────────────────────┐
│  moonshot-local FastAPI (port 8080) │
│  ┌────────────────────────────────┐ │
│  │ 1. Parse OpenAI-style request  │ │
│  │ 2. Detect search keywords      │ │
│  └────────────┬───────────────────┘ │
│               │                      │
│  ┌────────────▼───────────────────┐ │
│  │ 3. Selenium + Firefox          │ │
│  │    → Google search             │ │
│  │    → Scrape results            │ │
│  └────────────┬───────────────────┘ │
│               │                      │
│  ┌────────────▼───────────────────┐ │
│  │ 4. Inject results into prompt  │ │
│  └────────────┬───────────────────┘ │
└───────────────┼──────────────────────┘
                │
┌───────────────▼──────────────────────┐
│  Ollama (port 11434)                 │
│  Model: llama3.2:3b                  │
└───────────────┬──────────────────────┘
                │
┌───────────────▼──────────────────────┐
│  OpenAI-compatible SSE stream        │
│  back to Avante                      │
└──────────────────────────────────────┘
```

## What's Next

After you verify v1 works, you can:

1. **Upgrade model** → Better code quality
2. **Add caching** → Faster repeat searches
3. **Add page scraping** → Full article content
4. **Add reranking** → Better result relevance
5. **Support DuckDuckGo** → Alternative search
6. **Build Morph adapter** → Enable Fast Apply

## Getting Help

Check logs for errors:
```bash
# If running directly
# Logs print to console

# If running as systemd service
sudo journalctl -u moonshot-local -f
```

Common log patterns:
- `Search triggered` → Web search activated
- `Found N results` → Scraping succeeded
- `WebDriver error` → Browser/Selenium issue
- `LLM error` → Ollama connection problem

## Summary

**Start server:**
```bash
./start.sh
```

**Test:**
```bash
./test_api.sh
# or
python example_client.py
```

**Use with Avante:**
1. Configure provider in Neovim
2. Set `MOONSHOT_LOCAL_API_KEY`
3. Use Avante normally
4. Search triggers on keywords

**Done!** 🚀

