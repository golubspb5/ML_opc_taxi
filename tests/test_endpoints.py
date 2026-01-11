import pytest
import requests
import time

BASE_URL = "http://localhost:32000"

def wait_for_service(timeout=15):
    """Ждём пока сервис поднимется внутри Docker-контейнера."""
    for _ in range(timeout):
        try:
            r = requests.get(f"{BASE_URL}/")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def test_service_starts():
    assert wait_for_service(), "API service did not start in time"


def test_root_ok():
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "Uber" in body["message"]


def test_predict_real_model():
    payload = {
        "data": [{
            "pickup_latitude": 40.7,
            "pickup_longitude": -73.9,
            "dropoff_latitude": 40.8,
            "dropoff_longitude": -74.0,
            "passenger_count": 1
        }]
    }

    resp = requests.post(f"{BASE_URL}/api/predict/", json=payload)

    assert resp.status_code == 200, f"API returned {resp.status_code}: {resp.text}"

    data = resp.json()
    assert "predictions" in data
    assert isinstance(data["predictions"], list)
    assert isinstance(data["predictions"][0], float)
