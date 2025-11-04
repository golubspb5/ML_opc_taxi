# Module 6 Taxi App

## Быстрый старт

- **Требования**: Python 3.12 (см. `.python-version`), macOS/zsh
- **Путь проекта**: `<path_to_project>`

### 1) Установка окружения
```bash
cd <path_to_project>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Запуск API
Вариант A (рекомендуется, с авто‑перезапуском):
```bash
cd <path_to_project>
source .venv/bin/activate
uvicorn main:app --app-dir <path_to_project>/src/service --host 0.0.0.0 --port 32000 --reload
```

Вариант B (через модуль Python):
```bash
cd <path_to_project>
source .venv/bin/activate
python -m src.service.main  
```

Проверка:
```bash
curl -s http://127.0.0.1:32000/
```
Документация Swagger будет по адресу:
- `http://127.0.0.1:32000/docs`

Пример запроса на предсказание:
```bash
curl -s -X POST http://127.0.0.1:32000/api/predict/ \
  -H 'Content-Type: application/json' \
  -d '{
        "data": [
          {
            "pickup_latitude": 40.7614327,
            "pickup_longitude": -73.9798156,
            "dropoff_latitude": 40.6413111,
            "dropoff_longitude": -73.7781391,
            "passenger_count": 2
          }
        ]
      }'
```

UI-форма (простая HTML):
- `http://127.0.0.1:32000/predict/form/`

### 3) Обучение модели
Скрипт обучения читает датасет `src/uber.csv` и сохраняет модель в `src/service/model.pkl`.

Быстрый запуск по умолчанию:
```bash
cd <path_to_project>
source .venv/bin/activate
python <path_to_project>/src/service/train_and_save_model.py
```

С указанием параметров:
```bash
python <path_to_project>/src/service/train_and_save_model.py \
  --csv <path_to_project>/src/uber.csv \
  --output <path_to_project>/src/service/model.pkl \
  --test-size 0.2 \
  --random-state 42
```

- **Ожидаемые колонки** в CSV: `pickup_latitude`, `pickup_longitude`, `dropoff_latitude`, `dropoff_longitude`, `passenger_count`, таргет — `fare_amount`.
- После обучения сервис автоматически начнёт использовать обновлённый `model.pkl` при следующем запуске.

### 4) Полезное
- Установка зависимостей повторно: `pip install -r requirements.txt`
- Запуск тестов: `pytest`