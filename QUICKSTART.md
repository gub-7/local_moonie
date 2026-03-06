# Quick Setup Guide

## 1. Install Dependencies

```bash
# Arch Linux
sudo pacman -S firefox geckodriver python python-pip

# Install Python packages
pip install -e .
```

## 2. Configure

```bash
# Copy example env
cp .env.example .env

# Edit .env (optional, defaults should work)
nano .env
```

Key settings:
- `OLLAMA_HOST=http://127.0.0.1:11434` (your existing Ollama)
- `OLLAMA_MODEL=llama3.2:3b` (your existing model)
- `API_KEY=your-secret-key-here` (set this!)

## 3. Start Ollama (if not running)

```bash
ollama serve
```

## 4. Start moonshot-local

```bash
./start.sh
```

Or manually:
```bash
python -m moonshot_local.app.main
```

## 5. Test

```bash
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
./test_api.sh
```

## 6. Configure Avante

Add to your Neovim config:

```lua
-- See avante_config.lua for full example
providers = {
  moonshot_local = {
    __inherited_from = "openai",
    endpoint = "http://127.0.0.1:8080/v1",
    api_key_name = "MOONSHOT_LOCAL_API_KEY",
    model = "moonshot-local",
  },
}
```

Set environment variable:
```bash
export MOONSHOT_LOCAL_API_KEY=your-secret-key-here
```

## 7. Use in Avante

Open Neovim and:
- Normal coding prompts → uses llama3.2:3b
- Prompts with "latest", "docs", "search" → triggers Firefox search → augmented prompt → llama3.2:3b

## Troubleshooting

**Ollama not found:**
```bash
curl http://127.0.0.1:11434/api/tags
# Should return JSON with your models
```

**geckodriver not found:**
```bash
geckodriver --version
# Should print version
```

**Firefox opens but search fails:**
- Set `HEADLESS_BROWSER=false` in .env
- Manually accept Google consent if needed
- Browser profile persists for future runs

**Want better model:**
```bash
ollama pull qwen2.5-coder:14b
# Update OLLAMA_MODEL in .env
```

## Architecture

```
Avante → localhost:8080 → search decision → Firefox/Selenium → 
Google → scrape results → inject into prompt → Ollama → 
stream response → Avante
```

Done! 🚀

