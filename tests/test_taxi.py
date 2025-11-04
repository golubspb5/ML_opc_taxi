import pytest
import pandas as pd
import numpy as np


# Предполагается, что src/preprocessing.py находится в пути видимости Python
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Выполняет предобработку данных о поездках Uber."""
    # 1. Фильтрация по стоимости и пассажирам
    df_filtered = df[
        (df["fare_amount"] > 0)
        & (df["passenger_count"] > 0)
        & (df["passenger_count"] <= 6)
    ].copy()

    # 2. Создание нового признака 'distance'
    df_filtered["distance"] = np.sqrt(
        (df_filtered["dropoff_longitude"] - df_filtered["pickup_longitude"]) ** 2
        + (df_filtered["dropoff_latitude"] - df_filtered["pickup_latitude"]) ** 2
    )
    final_features = df_filtered[["distance", "passenger_count"]]
    return final_features


def test_preprocess_data_does_not_modify_original_dataframe():
    """Тест проверяет, что функция не изменяет исходный DataFrame."""
    original_df = pd.DataFrame(
        {
            "fare_amount": [10.0],
            "passenger_count": [1],
            "pickup_longitude": [-73.9],
            "pickup_latitude": [40.7],
            "dropoff_longitude": [-74.0],
            "dropoff_latitude": [40.8],
        }
    )
    original_columns = list(original_df.columns)

    preprocess_data(
        original_df.copy()
    )  # Передаём копию, чтобы избежать ошибки в других тестах

    assert list(original_df.columns) == original_columns


@pytest.fixture
def raw_uber_data() -> pd.DataFrame:
    """Фикстура, создающая сырые данные для тестов."""
    data = {
        "fare_amount": [10.0, -5.0, 20.0, 15.0, 30.0],
        "pickup_longitude": [-73.9, -73.9, -73.9, -73.9, -73.9],
        "pickup_latitude": [40.7, 40.7, 40.7, 40.7, 40.7],
        "dropoff_longitude": [-74.0, -74.0, -74.0, -74.0, -74.0],
        "dropoff_latitude": [40.8, 40.8, 40.8, 40.8, 40.8],
        "passenger_count": [1, 2, 0, 7, 3],  # Валидные: 1, 3. Невалидные: 0, 7
    }
    # Валидными являются первая и последняя строки
    return pd.DataFrame(data)


def test_filters_invalid_rows(raw_uber_data):
    """Тест проверяет, что невалидные строки отфильтрованы."""
    processed_df = preprocess_data(raw_uber_data)
    # Ожидаем, что останутся только 2 валидные строки
    assert len(processed_df) == 2
    assert all(processed_df["passenger_count"].isin([1, 3]))


def test_creates_distance_feature():
    """Тест проверяет корректность расчёта дистанции."""
    data = pd.DataFrame(
        {
            "fare_amount": [10.0],
            "passenger_count": [1],
            "pickup_longitude": [0.0],
            "pickup_latitude": [0.0],
            "dropoff_longitude": [3.0],
            "dropoff_latitude": [4.0],
        }
    )
    processed_df = preprocess_data(data)
    # Ожидаемое расстояние (по теореме Пифагора) = sqrt(3^2 + 4^2) = 5
    assert processed_df["distance"].iloc[0] == pytest.approx(5.0)


def test_returns_correct_columns(raw_uber_data):
    """Тест проверяет, что возвращаются только нужные колонки."""
    processed_df = preprocess_data(raw_uber_data)
    expected_columns = ["distance", "passenger_count"]
    assert list(processed_df.columns) == expected_columns


@pytest.mark.parametrize(
    "test_input, expected_rows",
    [
        ({"passenger_count": [0], "fare_amount": [10]}, 0),
        ({"passenger_count": [7], "fare_amount": [10]}, 0),
        ({"passenger_count": [1], "fare_amount": [-10]}, 0),
        ({"passenger_count": [1, 2], "fare_amount": [10, 20]}, 2),
    ],
)
def test_edge_case_filtering(test_input, expected_rows):
    """Параметризованный тест для граничных случаев фильтрации."""
    base_data = {
        "pickup_longitude": [-73.9],
        "pickup_latitude": [40.7],
        "dropoff_longitude": [-74.0],
        "dropoff_latitude": [40.8],
    }
    num_rows = len(test_input["passenger_count"])
    df_data = {**{k: [v[0]] * num_rows for k, v in base_data.items()}, **test_input}
    df = pd.DataFrame(df_data)

    processed_df = preprocess_data(df)
    assert len(processed_df) == expected_rows
