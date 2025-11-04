import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Выполняет базовую очистку данных:
    - Удаляет строки с пропущенными значениями.
    - Фильтрует выбросы по стоимости, количеству пассажиров и координатам.
    """
    df = df.dropna()
    df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 100)]
    df = df[(df["passenger_count"] > 0) & (df["passenger_count"] < 7)]
    df = df[
        (df["pickup_longitude"] > -75)
        & (df["pickup_longitude"] < -73)
        & (df["pickup_latitude"] > 40)
        & (df["pickup_latitude"] < 42)
        & (df["dropoff_longitude"] > -75)
        & (df["dropoff_longitude"] < -73)
        & (df["dropoff_latitude"] > 40)
        & (df["dropoff_latitude"] < 42)
    ]
    return df


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Подготавливает финальные признаки для модели.

    В данном случае, мы используем те же признаки, что и на входе,
    но эта функция является точкой для будущего расширения
    (например, добавления feature engineering).
    """
    # Пока что просто выбираем нужные колонки
    features = df[
        [
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "passenger_count",
        ]
    ]
    return features


def get_target(df: pd.DataFrame) -> pd.Series:
    """
    Возвращает целевую переменную.
    """
    return df["fare_amount"]
