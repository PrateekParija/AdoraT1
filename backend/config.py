# backend/config.py
import os
from pathlib import Path

# Directories (relative to project root by default)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", DATA_DIR / "uploads"))
RENDER_DIR = Path(os.getenv("RENDER_DIR", DATA_DIR / "renders"))
AUDIT_LOG_DIR = Path(os.getenv("AUDIT_LOG_DIR", DATA_DIR / "audit_logs"))

# App host/port
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Feature flags
ENABLE_SD = bool(os.getenv("ENABLE_SD", "0") in ("1", "true", "True"))
USE_OLLAMA = bool(os.getenv("USE_OLLAMA", "0") in ("1", "true", "True"))
ENABLE_DALLE = bool(os.getenv("ENABLE_DALLE", "0") in ("1", "true", "True"))

# SD model / LLM config
SD_MODEL_ID = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# File size limits
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE", "512000"))  # default 500 KiB

# DB
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "retail_tool.db"))

# Ensure directories exist
for d in (UPLOAD_DIR, RENDER_DIR, AUDIT_LOG_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
