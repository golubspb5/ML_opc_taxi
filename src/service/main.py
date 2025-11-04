from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from schemas import BatchPredictionRequest, PredictionResponse
from predictor import load_model

# Инициализация приложения с метаданными для документации
app = FastAPI(
    title="Uber Price Predictor API",
    description="Предскажи цену поездки в Uber на основе градиентного бустинга.",
    version="1.0.0",
    contact={
        "name": "Your Name",  # Используйте общее имя или организации, предоставляющей сервис
        "email": "your_email@example.com",  # Общий email
    },
)

# Загрузка модели при старте сервера (выполняется один раз)
model = load_model()


# Маршрут для проверки работоспособности сервиса
@app.get("/", tags=["Health Check"])
def read_root():
    return {"message": "🚗 Uber Price Predictor is running!"}


# Основной маршрут для получения предсказаний
@app.post("/api/predict/", response_model=PredictionResponse, tags=["Predictions"])
def predict(request: BatchPredictionRequest):
    try:
        # Преобразуем список словарей в список списков значений
        features_list = []
        for item in request.data:
            features = [
                item.pickup_latitude,
                item.pickup_longitude,
                item.dropoff_latitude,
                item.dropoff_longitude,
                item.passenger_count,
            ]
            features_list.append(features)

        predictions = model.predict(features_list)
        formatted_predictions = [f"{p:.2f} $" for p in predictions]
        print(formatted_predictions)
        return {"predictions": formatted_predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {str(e)}")


# Форма для заполнения данных
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
        
        // Получаем объект и конвертируем значения в нужные типы
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
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: [data] })  // Обязательно массив внутри data
        });

        if (!response.ok) {
            const errorData = await response.json();
            document.getElementById('result').innerText = 
                'Ошибка: ' + (errorData.detail || 'Неизвестная ошибка');
            return;
        }

        const result = await response.json();
        document.getElementById('result').innerText = 
            'Прогнозируемая цена: $' + result.predictions[0];
    });
</script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=32000, workers=1)
