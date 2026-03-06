"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Search for env file in multiple locations
_env_file_locations = [
    Path.cwd() / ".env",  # Current directory (development)
    Path("/etc/local-moonie/config.env"),  # System-wide installation
]

_loaded_env_file = None
for env_path in _env_file_locations:
    if env_path.exists():
        load_dotenv(env_path)
        _loaded_env_file = str(env_path.absolute())
        break


class Config:
    """Application configuration."""
    
    # Ollama backend
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large:latest")
    
    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8080"))
    API_KEY: str = os.getenv("API_KEY", "")
    
    # Search
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "10"))
    HEADLESS_BROWSER: bool = os.getenv("HEADLESS_BROWSER", "false").lower() == "true"
    
    # Model exposed to Avante
    EXPOSED_MODEL: str = "moonshot-local"

    @staticmethod
    def get_env_file_path() -> str | None:
        """Return the path of the loaded env file, or None if no file was loaded."""
        return _loaded_env_file


config = Config()

