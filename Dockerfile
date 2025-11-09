
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 32000

CMD ["uvicorn", "main:app", "--app-dir", "src/service", "--host", "0.0.0.0", "--port", "32000"]
