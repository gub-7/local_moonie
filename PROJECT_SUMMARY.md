# Moonshot-Local Project Summary

## What is this?

A local OpenAI-compatible API proxy that gives Avante.nvim web search capabilities using:
- **Firefox + Selenium** for Google search
- **Ollama** (your existing llama3.2:3b) for LLM generation
- **FastAPI** for OpenAI-compatible endpoints

## Why?

Moonshot/Kimi API has built-in web search, but it's cloud-based. This replicates that locally while keeping your code and queries private.

## Key Files

```
moonshot_local/
├── app/
│   ├── main.py              # FastAPI routes (/v1/models, /v1/chat/completions)
│   ├── schemas.py           # Pydantic models (OpenAI-compatible)
│   ├── config.py            # Configuration from .env
│   ├── browser.py           # Selenium Firefox manager
│   ├── search.py            # Google search scraper
│   ├── search_decider.py    # Decides when to search
│   ├── prompting.py         # Injects search results into prompt
│   ├── llm.py               # Ollama adapter
│   └── sse.py               # SSE streaming formatter
├── __init__.py
│
pyproject.toml               # Dependencies
.env.example                 # Configuration template
README.md                    # Full documentation
INSTALL.md                   # Detailed installation guide
QUICKSTART.md                # Quick setup steps
start.sh                     # Quick start script
test_api.sh                  # Test script
example_client.py            # Python example client
avante_config.lua            # Avante.nvim config example
moonshot-local.service       # systemd service file
```

## How It Works

### 1. Normal Coding Prompt

```
User in Avante: "Write quicksort in Python"
  ↓
moonshot-local: No search keywords detected
  ↓
Ollama (llama3.2:3b): Generate code
  ↓
Stream back to Avante
```

### 2. Search-Enabled Prompt

```
User in Avante: "What are the latest features in FastAPI?"
  ↓
moonshot-local: Detected "latest" keyword
  ↓
Firefox + Selenium: Search Google for query
  ↓
Scrape top 5 results (title, URL, snippet)
  ↓
Inject into prompt as context:
  "WEB_RESULTS:
   [1] FastAPI 0.109.0 Release
   URL: https://...
   Snippet: New features include..."
  ↓
Ollama (llama3.2:3b): Generate answer with web context
  ↓
Stream back to Avante with citations
```

## API Endpoints

### GET /v1/models
Returns available models (OpenAI-compatible).

### POST /v1/chat/completions
Main endpoint. Accepts:
- `model`: "moonshot-local"
- `messages`: Array of {role, content}
- `stream`: true/false
- `temperature`, `max_tokens`: Optional

Returns OpenAI-compatible response (streaming or non-streaming).

### GET /health
Health check.

## Search Trigger Keywords

Search activates when prompt contains:
- `latest`, `current`, `today`, `recent`, `search`
- `docs`, `documentation`, `release notes`
- `version`, `pricing`, `news`
- `what is`, `how to`, `tutorial`

## Configuration (.env)

```bash
# Ollama backend (your existing setup)
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b

# Server
HOST=127.0.0.1
PORT=8080
API_KEY=your-secret-key-here

# Search
MAX_SEARCH_RESULTS=5
SEARCH_TIMEOUT=10
HEADLESS_BROWSER=false
```

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Configure
cp .env.example .env
nano .env  # Set API_KEY

# 3. Start
./start.sh

# 4. Test
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
./test_api.sh
```

## Avante Integration

```lua
-- In your Neovim config
providers = {
  moonshot_local = {
    __inherited_from = "openai",
    endpoint = "http://127.0.0.1:8080/v1",
    api_key_name = "MOONSHOT_LOCAL_API_KEY",
    model = "moonshot-local",
  },
}
```

```bash
# Set env var
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

## Dependencies

**System:**
- Firefox
- geckodriver
- Python 3.11+
- Ollama (already running)

**Python:**
- FastAPI
- uvicorn
- Pydantic
- Selenium
- httpx
- python-dotenv

## Performance

- **Normal prompts:** ~Same as direct Ollama
- **Search prompts:** +2-5 seconds for Firefox/scraping
- **Model quality:** llama3.2:3b is fast but weak
  - Upgrade to qwen2.5-coder:14b for better coding

## Limitations

- Single-user (serialized browser access)
- Google DOM changes can break scraping
- No Fast Apply (requires separate Morph service)
- llama3.2:3b is small model

## Troubleshooting

**Server won't start:**
- Check Ollama is running: `curl http://127.0.0.1:11434/api/tags`
- Check port 8080 is free: `sudo lsof -i :8080`

**Search fails:**
- Set `HEADLESS_BROWSER=false` to see Firefox
- Manually accept Google consent if needed
- Check geckodriver is installed: `geckodriver --version`

**Avante can't connect:**
- Verify server: `curl http://127.0.0.1:8080/health`
- Check API key matches in .env and shell

## Upgrading Model

```bash
# Pull better model
ollama pull qwen2.5-coder:14b

# Update .env
OLLAMA_MODEL=qwen2.5-coder:14b

# Restart server
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Avante.nvim                          │
│                  (Neovim coding assistant)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST /v1/chat/completions
                         │ (OpenAI-compatible request)
                         │
┌────────────────────────▼────────────────────────────────────┐
│              moonshot-local FastAPI Server                  │
│                    (localhost:8080)                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Request Handler (main.py)                        │  │
│  │     • Parse OpenAI request                           │  │
│  │     • Verify API key                                 │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  2. Search Decision Engine (search_decider.py)       │  │
│  │     • Check for keywords: "latest", "docs", etc.     │  │
│  │     • Generate search queries                        │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│         ┌────────────┴────────────┐                        │
│         │ Search needed?          │                        │
│         └─────┬──────────────┬────┘                        │
│              YES            NO                              │
│               │              │                              │
│  ┌────────────▼────────┐    │                              │
│  │  3. Selenium Search │    │                              │
│  │     (search.py)     │    │                              │
│  │  ┌──────────────┐   │    │                              │
│  │  │   Firefox    │   │    │                              │
│  │  │ + geckodriver│   │    │                              │
│  │  └──────┬───────┘   │    │                              │
│  │         │           │    │                              │
│  │  ┌──────▼───────┐   │    │                              │
│  │  │ Google Search│   │    │                              │
│  │  └──────┬───────┘   │    │                              │
│  │         │           │    │                              │
│  │  ┌──────▼───────┐   │    │                              │
│  │  │Scrape Results│   │    │                              │
│  │  │ • Title      │   │    │                              │
│  │  │ • URL        │   │    │                              │
│  │  │ • Snippet    │   │    │                              │
│  │  └──────┬───────┘   │    │                              │
│  └─────────┼───────────┘    │                              │
│            │                │                              │
│  ┌─────────▼────────────────▼──────────────────────────┐  │
│  │  4. Prompt Augmentation (prompting.py)              │  │
│  │     • Inject WEB_RESULTS into system message        │  │
│  │     • Preserve original conversation                │  │
│  └─────────┬───────────────────────────────────────────┘  │
└────────────┼──────────────────────────────────────────────┘
             │
             │ Augmented prompt
             │
┌────────────▼──────────────────────────────────────────────┐
│                  Ollama (llm.py)                          │
│                localhost:11434                            │
│                                                           │
│  Model: llama3.2:3b                                       │
│  • Chat generation with web context                       │
│  • Stream or non-stream mode                              │
└────────────┬──────────────────────────────────────────────┘
             │
             │ Token stream
             │
┌────────────▼──────────────────────────────────────────────┐
│              SSE Formatter (sse.py)                       │
│  • Convert Ollama format to OpenAI format                 │
│  • Generate SSE chunks                                    │
│  • Add finish_reason                                      │
└────────────┬──────────────────────────────────────────────┘
             │
             │ OpenAI-compatible SSE stream:
             │ data: {"choices":[{"delta":{"content":"..."}}]}
             │
┌────────────▼──────────────────────────────────────────────┐
│                     Avante.nvim                           │
│  • Parse SSE stream                                       │
│  • Display in Neovim buffer                               │
│  • Show citations from WEB_RESULTS                        │
└───────────────────────────────────────────────────────────┘
```

## Testing Flow

```bash
# Terminal 1: Start server
./start.sh

# Terminal 2: Run tests
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here

# Test 1: Health
curl http://127.0.0.1:8080/health

# Test 2: Models
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer $MOONSHOT_LOCAL_API_KEY"

# Test 3: Simple chat (no search)
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer $MOONSHOT_LOCAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"moonshot-local","messages":[{"role":"user","content":"Hello"}],"stream":false}'

# Test 4: Search-enabled chat
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer $MOONSHOT_LOCAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"moonshot-local","messages":[{"role":"user","content":"latest Python features"}],"stream":true}'

# Or use provided scripts
./test_api.sh
python example_client.py
```

## Security Notes

- API key required by default (set in .env)
- Binds to localhost by default (not exposed to network)
- For production: use HTTPS reverse proxy, stronger auth

## Future Enhancements

**v2 roadmap:**
- [ ] Result caching (Redis/SQLite)
- [ ] DuckDuckGo/Brave Search support
- [ ] Full page content extraction
- [ ] Local reranker for results
- [ ] Multi-browser pool
- [ ] Tool-call emulation
- [ ] Morph-compatible Fast Apply service
- [ ] Embeddings endpoint for RAG

## Credits

Built for Avante.nvim with:
- FastAPI (web framework)
- Selenium (browser automation)
- Ollama (local LLM)
- Your existing setup: llama3.2:3b on RTX 3080

## License

MIT

---

**Status:** ✅ Complete and ready to use

**Next steps:**
1. `pip install -e .`
2. `cp .env.example .env` (edit API_KEY)
3. `./start.sh`
4. Configure Avante
5. Code with web search! 🚀

