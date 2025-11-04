FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python src/service/train_and_save_model.py

EXPOSE 32000

CMD ["uvicorn", "src.service.main:app", "--host", "0.0.0.0", "--port", "32000"]
