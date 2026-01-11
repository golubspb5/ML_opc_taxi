from pathlib import Path
from functools import lru_cache
import os
import joblib

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

def resolve_model_path() -> Path:
    p = os.getenv("MODEL_PATH")
    return Path(p) if p else DEFAULT_MODEL_PATH

@lru_cache(maxsize=1)
def load_model(path: Path | None = None):
    path = Path(path) if path else resolve_model_path()
    return joblib.load(path)
