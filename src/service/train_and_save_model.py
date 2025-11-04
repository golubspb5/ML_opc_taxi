import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from processing import clean_data, get_target, prepare_features

# Определяем путь к текущему файлу, чтобы найти CSV и место для сохранения модели
CURRENT_DIR = Path(__file__).parent
DEFAULT_DATA_PATH = CURRENT_DIR.parent / "uber.csv"
DEFAULT_MODEL_PATH = CURRENT_DIR / "model.pkl"


def train_and_save_model(
    data_path: Path, model_path: Path, test_size: float, random_state: int
):  # ИЗМЕНЕНО
    """
    Функция для обучения и сохранения модели градиентного бустинга.
    """
    print("Starting model training...")

    # 1. Загрузка данных
    try:
        df_raw = pd.read_csv(data_path, nrows=100_000)
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    # 2. Очистка данных (используем централизованную функцию)
    df_cleaned = clean_data(df_raw)

    # 3. Подготовка фичей и таргета
    X = prepare_features(df_cleaned)
    y = get_target(df_cleaned)

    # 4. Обучающая и тестовая выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 5. Инициализация и обучение модели
    print("Training Gradient Boosting Regressor...")
    model = GradientBoostingRegressor(
        n_estimators=100, learning_rate=0.1, max_depth=3, random_state=random_state
    )
    model.fit(X_train, y_train)

    # 6. Оценка модели
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Model evaluation finished. Test RMSE: {rmse:.2f}")

    # 7. Сохранение модели
    joblib.dump(model, model_path)
    print(f"Model successfully saved to {model_path}")


# Добавляем возможность запуска из командной строки с параметрами
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and save the model.")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to the training data CSV file.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Path to save the trained model.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of the dataset to include in the test split.",
    )
    parser.add_argument(
        "--random-state", type=int, default=42, help="Random state for reproducibility."
    )

    args = parser.parse_args()

    train_and_save_model(
        data_path=args.data_path,
        model_path=args.model_path,
        test_size=args.test_size,
        random_state=args.random_state,
    )
