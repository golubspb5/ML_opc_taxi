import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def train(csv_path: Path, output_path: Path, test_size: float, random_state: int) -> None:
    # 1) Загрузка данных
    df = pd.read_csv(csv_path)

    features = [
        "pickup_latitude",
        "pickup_longitude",
        "dropoff_latitude",
        "dropoff_longitude",
        "passenger_count",
    ]
    target = "fare_amount"

    # 2) Удаляем строки с NaN в таргете
    df = df.dropna(subset=[target])

    # 3) Разделяем на X/y
    X = df[features]
    y = df[target]

    # 4) Импутация пропусков в признаках медианами
    imputer = SimpleImputer(strategy="median")
    X = pd.DataFrame(imputer.fit_transform(X), columns=features)

    # 5) Трейн/тест
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 6) Обучение
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 7) Оценка
    y_pred = model.predict(X_test)
    metrics = {
        "mse": float(mean_squared_error(y_test, y_pred)),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
    }

    # 8) Сохранение модели
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)

    # 9) Сохранение метрик (как артефакт)
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)
    (metrics_dir / "train_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    print(f"Model saved to {output_path}")
    print(f"Metrics: {metrics}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    train(Path(args.csv), Path(args.output), args.test_size, args.random_state)


if __name__ == "__main__":
    main()
