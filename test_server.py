from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.1.0"

def test_payload_endpoint():
    response = client.get("/api/payload")
    assert response.status_code == 200
    data = response.json()
    assert "temperature_c" in data
    assert data["status"] == "PAYLOAD_NOMINAL"

def test_mission_endpoint():
    response = client.get("/api/mission")
    assert response.status_code == 200
    data = response.json()
    assert data["mission_name"] == "ODYSSEY-1-ADVANCED"
    assert len(data["waypoints"]) > 0

def test_failover_endpoint():
    response = client.get("/api/failover")
    assert response.status_code == 200
    data = response.json()
    assert "active_station" in data
    assert "latency_ms" in data
