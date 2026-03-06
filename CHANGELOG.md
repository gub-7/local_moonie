# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-06

### Added
- Initial release of moonshot-local
- OpenAI-compatible `/v1/models` endpoint
- OpenAI-compatible `/v1/chat/completions` endpoint with streaming support
- Automatic web search detection based on keywords
- Firefox/Selenium Google search integration
- Search result injection into prompt context
- Ollama backend adapter for local LLM generation
- Graceful degradation when search fails
- Browser session management with automatic restart
- Configuration via environment variables
- Health check endpoint
- CLI entry point: `moonshot-local`
- Support for Avante.nvim as custom OpenAI-compatible provider
- Comprehensive documentation and examples

### Features
- **Search Keywords**: Triggers on "latest", "current", "docs", "how to", etc.
- **Streaming**: Full SSE streaming support for real-time responses
- **Local-first**: All processing happens locally (Ollama + Firefox)
- **API Key Auth**: Optional API key authentication
- **Configurable**: Browser headless mode, search timeouts, result limits

### Documentation
- Complete README with installation and usage instructions
- Example Avante.nvim configuration
- Python example client
- Shell test scripts
- systemd service file for deployment

[0.1.0]: https://github.com/yourusername/moonshot-local/releases/tag/v0.1.0

