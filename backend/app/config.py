import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "tco.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

LOGO_PATH = Path(__file__).parent / "pdf" / "assets" / "poweron_logo.png"
