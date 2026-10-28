from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_fdir_state_vector():
    response = client.get("/api/fdir/state-vector")
    assert response.status_code == 200
    data = response.json()
    assert "system_health" in data
    assert "subsystems" in data
    assert "imu_ekf" in data["subsystems"]

def test_fdir_override_action():
    response = client.post("/api/fdir/override", json={"subsystem": "imu_ekf", "action": "ISOLATE"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["target_subsystem"] == "imu_ekf"

def test_tactical_hd_map_telemetry():
    response = client.get("/api/tactical/map-telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "map_provider" in data
    assert "current_position" in data
    assert "ground_track_history" in data
    assert len(data["ground_track_history"]) > 0
