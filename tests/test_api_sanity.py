"""
Модуль интеграционных тестов для FastAPI приложения.
Тесты проверяют основные endpoints (корневой URL и prediction API) без реальной модели.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def get_client():
    """
    Создаёт и возвращает тестовый клиент FastAPI с замоканной моделью машинного обучения.
    
    Зачем это нужно:
    - Мы не хотим загружать реальную модель во время тестов (это медленно)
    - Мы хотим изолировать тесты API от работы модели
    - Мы контролируем поведение модели для предсказуемых тестов
    
    Returns:
        TestClient: тестовый клиент FastAPI с подменённой моделью
    """
    # Патчим (временно подменяем) функцию load_model в модуле src.service.main
    with patch("src.service.main.load_model") as mock_load_model:
        # Создаём фейковую (mock) модель которая имитирует поведение реальной
        fake_model = MagicMock()
        
        # Настраиваем модель так, чтобы она всегда возвращала предсказание 42.5
        # Это тестовое значение которое мы будем проверять в тестах
        fake_model.predict.return_value = [42.5]
        
        # Говорим mock'у, что при вызове load_model() он должен вернуть нашу фейковую модель
        mock_load_model.return_value = fake_model

        # Импортируем приложение ПОСЛЕ мока, чтобы mock успел подмениться
        from src.service.main import app   
        
        # Создаём тестовый клиент для отправки HTTP запросов к нашему приложению
        return TestClient(app)


def test_root_endpoint():
    """
    Тестирует корневой endpoint приложения (/).
    
    Проверяет что:
    - Сервер отвечает на GET запрос к корневому URL
    - Ответ содержит ожидаемую структуру данных
    - В сообщении есть ключевое слово, подтверждающее что это нужное нам приложение
    """
    # Получаем тестовый клиент с замоканной моделью
    client = get_client()
    
    # Отправляем GET запрос к корневому URL приложения
    response = client.get("/")
    
    # Проверяем что сервер ответил статусом 200 (OK)
    assert response.status_code == 200, "Корневой endpoint должен возвращать статус 200"
    
    # Парсим JSON ответ и проверяем его содержание
    response_data = response.json()
    
    # Проверяем что в ответе есть поле 'message'
    assert "message" in response_data, "Ответ должен содержать поле 'message'"
    
    # Проверяем что в сообщении есть слово 'Uber' (идентификатор нашего сервиса)
    assert "Uber" in response_data["message"], "Сообщение должно идентифицировать сервис Uber"


def test_predict_endpoint_smoke_test():
    """
    Дымовой тест для endpoint предсказаний (/api/predict/).
    
    Проверяет базовую работоспособность API предсказаний в двух сценариях:
    1. Успешное предсказание когда модель доступна
    2. Ошибка когда модель недоступна
    
    Smoke test (дымовой тест) - это быстрая проверка что система вообще работает
    """
    # Получаем тестовый клиент с замоканной моделью
    client = get_client()

    # Подготавливаем тестовые данные для предсказания
    # Это пример координат поездки в Нью-Йорке:
    # - pickup: широта 40.7614 (район Манхэттен), долгота -73.9776
    # - dropoff: широта 40.6413 (аэропорт JFK), долгота -73.7781
    # - 2 пассажира
    test_payload = {
        "data": [{
            "pickup_latitude": 40.7614,      # Широта точки посадки
            "pickup_longitude": -73.9776,    # Долгота точки посадки  
            "dropoff_latitude": 40.6413,     # Широта точки высадки
            "dropoff_longitude": -73.7781,   # Долгота точки высадки
            "passenger_count": 2             # Количество пассажиров
        }]
    }

    # Отправляем POST запрос к API предсказаний с тестовыми данными
    response = client.post("/api/predict/", json=test_payload)

    # Проверяем что сервер ответил одним из ожидаемых статусов
    # 200 = OK (предсказание успешно)
    # 503 = Service Unavailable (модель недоступна)
    assert response.status_code in (200, 503), "API должен возвращать либо 200, либо 503 статус"

    # Парсим JSON ответ
    response_data = response.json()
    
    # Проверяем что ответ является словарем (а не списком или другим типом)
    assert isinstance(response_data, dict), "Ответ API должен быть словарем"

    # Анализируем ответ в зависимости от статуса
    if response.status_code == 200:
        # Сценарий успешного предсказания
        # Проверяем что в ответе есть поле 'predictions'
        assert "predictions" in response_data, "Успешный ответ должен содержать 'predictions'"
        
        # Дополнительная проверка: убедимся что predictions - это список
        assert isinstance(response_data["predictions"], list), "Predictions должен быть списком"
        
        # Дополнительная проверка: убедимся что список не пустой
        assert len(response_data["predictions"]) > 0, "Список predictions не должен быть пустым"
        
    else:
        # Сценарий когда модель недоступна (статус 503)
        # Проверяем что в ответе есть поле 'detail' с информацией об ошибке
        assert "detail" in response_data, "Ошибочный ответ должен содержать 'detail'"
        
        # Проверяем что сообщение об ошибке указывает на проблему с моделью
        assert "Model not found" in response_data["detail"], "Сообщение об ошибке должно указывать на отсутствие модели"


# Дополнительный тест для проверки различных сценариев ввода
def test_predict_with_multiple_rides():
    """
    Тестирует endpoint предсказаний с несколькими поездками в одном запросе.
    """
    client = get_client()

    # Тестовые данные с несколькими поездками
    test_payload = {
        "data": [
            {
                "pickup_latitude": 40.7589,    # Таймс-сквер
                "pickup_longitude": -73.9851,
                "dropoff_latitude": 40.6892,   # Статуя Свободы (паром)
                "dropoff_longitude": -74.0445,
                "passenger_count": 1
            },
            {
                "pickup_latitude": 40.7505,    # Пенсильванский вокзал
                "pickup_longitude": -73.9934,
                "dropoff_latitude": 40.7282,   # Ист-Виллидж
                "dropoff_longitude": -73.9842,
                "passenger_count": 3
            },
            {
                "pickup_latitude": 40.8176,    # Верхний Манхэттен
                "pickup_longitude": -73.9360,
                "dropoff_latitude": 40.7061,   # Уолл-стрит
                "dropoff_longitude": -74.0088,
                "passenger_count": 2
            }
        ]
    }

    response = client.post("/api/predict/", json=test_payload)
    
    # Проверяем успешный ответ
    assert response.status_code == 200, "Должен возвращаться статус 200 для валидных данных"
    
    response_data = response.json()
    assert "predictions" in response_data, "Ответ должен содержать predictions"
    
    # Проверяем что количество предсказаний соответствует количеству входных поездок
    assert len(response_data["predictions"]) == len(test_payload["data"]), \
        "Количество предсказаний должно совпадать с количеством входных данных"