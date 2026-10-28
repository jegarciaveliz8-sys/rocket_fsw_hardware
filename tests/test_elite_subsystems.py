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
    # Firmar comando
    res_sign = client.post("/api/security/sign-command", json={"command": "LAUNCH"})
    assert res_sign.status_code == 200
    sig_data = res_sign.json()
    assert sig_data["command"] == "LAUNCH"
    signature = sig_data["hmac_signature"]

    # Verificar comando con firma válida
    res_verify = client.post("/api/security/verify-command", json={"command": "LAUNCH", "signature": signature})
    assert res_verify.status_code == 200
    assert res_verify.json()["authenticated"] is True

    # Verificar con firma inválida
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
