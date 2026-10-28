from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_auth_rbac_token():
    response = client.post("/api/auth/token", json={"username": "jose", "role": "DIRECTOR"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "LAUNCH_ABORT" in data["permissions"]

def test_audit_logs_trail():
    response = client.get("/api/audit/logs")
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] > 0
    assert len(data["audit_logs"]) > 0

def test_network_impairment_simulation():
    response = client.post("/api/network-sim/impairment", json={"latency_ms": 120, "packet_loss_pct": 2.5})
    assert response.status_code == 200
    data = response.json()
    assert data["simulated_latency_ms"] == 120
    assert data["link_state"] == "NOMINAL"

def test_orbital_mechanics_window():
    response = client.post("/api/orbit/window", json={"target_altitude_km": 500.0, "inclination_deg": 51.6})
    assert response.status_code == 200
    data = response.json()
    assert data["target_altitude_km"] == 500.0
    assert "optimal_launch_utc" in data
