import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_CSV = Path(os.getenv("FEEDBACK_CSV", BASE_DIR / "feedback.csv"))
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

