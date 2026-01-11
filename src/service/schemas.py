from pydantic import BaseModel
from typing import List


class PredictionRequest(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    passenger_count: int


# Для списка запросов
class BatchPredictionRequest(BaseModel):
    data: List[PredictionRequest]


class PredictionResponse(BaseModel):
    predictions: List[float]
