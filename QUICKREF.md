# Quick Reference

## Installation

```bash
pip install moonshot-local
```

## Configuration

```bash
# Create config
cat > .env << EOF
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
API_KEY=your-secret-key-here
HEADLESS_BROWSER=false
EOF

# Set API key in environment
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

## Running

```bash
# Start server
moonshot-local

# Or with python
python -m moonshot_local.app.main
```

## Testing

```bash
# Health check
curl http://127.0.0.1:8080/health

# List models
curl http://127.0.0.1:8080/v1/models \
  -H "Authorization: Bearer your-secret-key-here"

# Chat (non-streaming)
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'

# Chat with search (streaming)
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-key-here" \
  -d '{
    "model": "moonshot-local",
    "messages": [{"role": "user", "content": "latest Python features"}],
    "stream": true
  }'
```

## Avante.nvim Config

```lua
providers = {
  moonshot_local = {
    __inherited_from = "openai",
    endpoint = "http://127.0.0.1:8080/v1",
    api_key_name = "MOONSHOT_LOCAL_API_KEY",
    model = "moonshot-local",
  },
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:3b` | Model to use |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8080` | Server port |
| `API_KEY` | (empty) | API key for auth |
| `MAX_SEARCH_RESULTS` | `5` | Max results per query |
| `SEARCH_TIMEOUT` | `10` | Search timeout (seconds) |
| `HEADLESS_BROWSER` | `false` | Hide Firefox window |

## Search Keywords

Search triggers on: `latest`, `current`, `today`, `recent`, `search`, `docs`, `documentation`, `release notes`, `version`, `pricing`, `news`, `what is`, `how to`, `tutorial`

## Troubleshooting

**Server won't start:**
```bash
# Check Ollama
curl http://127.0.0.1:11434/api/tags

# Check port
sudo lsof -i :8080
```

**Search fails:**
```bash
# Check geckodriver
geckodriver --version

# Check Firefox
firefox --version
```

**Avante can't connect:**
```bash
# Verify server
curl http://127.0.0.1:8080/health

# Check env var
echo $MOONSHOT_LOCAL_API_KEY
```

## Links

- GitHub: https://github.com/yourusername/moonshot-local
- PyPI: https://pypi.org/project/moonshot-local/
- Avante.nvim: https://github.com/yetone/avante.nvim
- Issues: https://github.com/yourusername/moonshot-local/issues

