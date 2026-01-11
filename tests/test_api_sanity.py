from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def get_client():
    """
    Создаём TestClient, предварительно замокав load_model()
    """
    with patch("src.service.main.load_model") as mock_load:
        fake_model = MagicMock()
        fake_model.predict.return_value = [11.11]
        mock_load.return_value = fake_model

        from src.service.main import app   
        return TestClient(app)


def test_root():
    client = get_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Uber" in resp.json().get("message", "")


def test_predict_smoke():
    client = get_client()

    payload = {
        "data": [{
            "pickup_latitude": 40.1,
            "pickup_longitude": -72.0,
            "dropoff_latitude": 40.2,
            "dropoff_longitude": -73.0,
            "passenger_count": 2
        }]
    }

    resp = client.post("/api/predict/", json=payload)

    assert resp.status_code in (200, 503)

    data = resp.json()
    assert isinstance(data, dict)

    if resp.status_code == 200:
        assert "predictions" in data
    else:
        assert "detail" in data
        assert "Model not found" in data["detail"]

