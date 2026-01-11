FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# curl для healthcheck-а
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt -q

COPY src /app/src

CMD ["uvicorn", "src.service.main:app", "--host", "0.0.0.0", "--port", "32000"]
