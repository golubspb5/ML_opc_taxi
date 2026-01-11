from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd

from src.service.schemas import BatchPredictionRequest, PredictionResponse
from src.service.predictor import load_model, resolve_model_path

# Инициализация приложения с метаданными
app = FastAPI(
    title="Uber Price Predictor API",
    description="Предскажи цену поездки в Uber на основе градиентного бустинга.",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "your_email@example.com",
    },
)


# Health-чек 
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "🚗 Uber Price Predictor is running!"}


# Основной эндпоинт предсказания
@app.post("/api/predict/", response_model=PredictionResponse, tags=["Predictions"])
def predict(request: BatchPredictionRequest):
    try:
        # Загружаем модель (если файл появится после обучения — подхватится)
        model = load_model()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Model not found at {resolve_model_path()}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки модели: {str(e)}")

    try:
        # Преобразуем входные данные в DataFrame
        df = pd.DataFrame([item.model_dump() for item in request.data])
        preds = model.predict(df)
        # Возвращаем просто числа без форматирования строки
        return {"predictions": [float(p) for p in preds]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")


# Простая HTML-форма для взаимодействия через браузер
@app.get("/predict/form/", response_class=HTMLResponse, tags=["UI"])
async def get_form():
    html_content = """
    <html>
        <head>
            <title>Расчет стоимости поездки на Uber</title>
            <style>
                body { font-family: Arial; padding: 20px; background-color: #f8f9fa; }
                h1 { color: #343a40; }
                label { display: block; margin-top: 10px; }
                input { width: 300px; padding: 5px; }
                button { margin-top: 15px; padding: 10px 20px; }
                .result { margin-top: 20px; font-size: 18px; color: green; }
            </style>
        </head>
        <body>
            <h1>Предиктор цены поездки</h1>
            <form id="predictForm">
                <label>Pickup Latitude:
                    <input type="number" step="any" name="pickup_latitude" required />
                </label>
                <label>Pickup Longitude:
                    <input type="number" step="any" name="pickup_longitude" required />
                </label>
                <label>Dropoff Latitude:
                    <input type="number" step="any" name="dropoff_latitude" required />
                </label>
                <label>Dropoff Longitude:
                    <input type="number" step="any" name="dropoff_longitude" required />
                </label>
                <label>Passenger Count:
                    <input type="number" min="1" max="10" name="passenger_count" required />
                </label>
                <button type="submit">Предсказать цену</button>
            </form>
            <div class="result" id="result"></div>

            <script>
            document.getElementById('predictForm').addEventListener('submit', async function (e) {
                e.preventDefault();
                const formData = new FormData(this);

                const data = {};
                formData.forEach((value, key) => {
                    if (key === 'passenger_count') {
                        data[key] = parseInt(value);
                    } else {
                        data[key] = parseFloat(value);
                    }
                });

                const response = await fetch('/api/predict/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data: [data] })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    document.getElementById('result').innerText =
                        'Ошибка: ' + (errorData.detail || 'Неизвестная ошибка');
                    return;
                }

                const result = await response.json();
                document.getElementById('result').innerText =
                     'Прогнозируемая цена: $' + Number(result.predictions[0]).toFixed(2);

            });
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# Запуск сервера (для локального дебага)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=32000, workers=1)
