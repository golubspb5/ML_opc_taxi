from pathlib import Path
import joblib


def load_model() -> object:
    return joblib.load(Path(__file__).resolve().parent / "model.pkl")
