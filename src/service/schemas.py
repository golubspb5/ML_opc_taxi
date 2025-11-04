from pydantic import BaseModel


class PredictionRequest(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    passenger_count: int


# Для списка запросов
class BatchPredictionRequest(BaseModel):
    data: list[PredictionRequest]


class PredictionResponse(BaseModel):
    predictions: list[str]
