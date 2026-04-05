import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

TASK_DB_PATH = PROJECT_ROOT / "data" / "tasks.db"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
RESULTS_DIR = PROJECT_ROOT / "results"
SESSIONS_FILE = SESSIONS_DIR / "session.json"
OPENCODE_CMD = "P:\\nodejs\\opencode.cmd"
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:5173"]
