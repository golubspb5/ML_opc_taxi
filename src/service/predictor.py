import os
from pathlib import Path

import joblib

MODEL_PATH = os.getenv("MODEL_PATH", Path(__file__).parent / "model.pkl")


def load_model() -> object:
    """
    Загружает модель из файла. Путь к файлу определяется
    переменной окружения MODEL_PATH.
    """
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded successfully from {MODEL_PATH}")
        return model
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        return None
