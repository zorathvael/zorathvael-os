from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["live_data_source"] == "binance-futures-public"


def test_root_disallows_mock_data():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["mock_data"] is False
