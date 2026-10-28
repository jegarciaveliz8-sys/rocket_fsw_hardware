from fastapi.testclient import TestClient
from server import app
import hmac
import hashlib

client = TestClient(app)

def test_monte_carlo_simulation():
    response = client.post("/api/monte-carlo/simulate", json={"runs": 50, "wind_variance_pct": 10.0})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["simulation_runs"] == 50
    assert "impact_dispersion_ellipse" in data

def test_security_hmac_lifecycle():
    res_sign = client.post("/api/security/sign-command", json={"command": "LAUNCH"})
    assert res_sign.status_code == 200
    sig_data = res_sign.json()
    assert sig_data["command"] == "LAUNCH"
    signature = sig_data["hmac_signature"]

    res_verify = client.post("/api/security/verify-command", json={"command": "LAUNCH", "signature": signature})
    assert res_verify.status_code == 200
    assert res_verify.json()["authenticated"] is True

    res_invalid = client.post("/api/security/verify-command", json={"command": "LAUNCH", "signature": "bad_signature"})
    assert res_invalid.status_code == 200
    assert res_invalid.json()["authenticated"] is False

def test_payload_science_telemetry():
    response = client.get("/api/science/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "radiation_sensor" in data
    assert "differential_pressure" in data
    assert "stage_separation" in data

def test_swarm_fleet_and_commands():
    res_fleet = client.get("/api/swarm/vehicles")
    assert res_fleet.status_code == 200
    assert res_fleet.json()["fleet_size"] == 3

    res_cmd = client.post("/api/swarm/command", json={"command": "RTL"})
    assert res_cmd.status_code == 200
    assert res_cmd.json()["broadcast_command"] == "RTL"

def test_timeseries_database_query():
    response = client.get("/api/timeseries/query?metric=altitude&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "altitude"
    assert len(data["data_points"]) == 5

def test_hardware_in_the_loop_simulation():
    res_conn = client.post("/api/hil/connect", json={"interface": "USB_UART_1", "baudrate": 921600})
    assert res_conn.status_code == 200
    assert res_conn.json()["hil_state"] == "CONNECTED"

    res_status = client.get("/api/hil/status")
    assert res_status.status_code == 200
    assert res_status.json()["hardware_in_loop"] is True
