from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.3.0"

def test_dashboard_endpoint():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "ODYSSEY-1 GCS - Mission Control Center" in response.text

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

def test_command_uplink():
    response = client.post("/api/command", json={"command": "ABORT", "target_module": "TVC_GIMBAL"})
    assert response.status_code == 200
    assert response.json()["status"] == "EXECUTED"

def test_export_logs():
    response = client.get("/api/logs/export")
    assert response.status_code == 200

def test_websocket_telemetry():
    with client.websocket_connect("/ws/telemetry") as websocket:
        data = websocket.receive_json()
        assert "altitude" in data
        assert "speed" in data
        assert "payload" in data
        assert "failover" in data
        assert "timestamp" in data
