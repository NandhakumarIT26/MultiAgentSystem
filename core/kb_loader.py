# kb_loader.py
import pandas as pd
from pathlib import Path
import os
# --- Absolute path fix ---
BASE_DIR = Path(os.path.dirname(__file__)).parent  # points to project root
KB_DIR = BASE_DIR / "KnowledgeBase"


def load_crop_data():
    return pd.read_csv(KB_DIR / "crop_data.csv")

def load_soil_data():
    return pd.read_csv(KB_DIR / "soil_data.csv")

def load_regional_data():
    # Note: filename in repo is 'regiona_data.csv' (typo). Prefer the correct name if present.
    regional_path = KB_DIR / "regional_data.csv"
    if not regional_path.exists():
        regional_path = KB_DIR / "regiona_data.csv"
    return pd.read_csv(regional_path)

def load_policy_data():
    return pd.read_csv(KB_DIR / "policy_data.csv")
