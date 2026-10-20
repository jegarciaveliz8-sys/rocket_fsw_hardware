import pytest
from fastapi.testclient import TestClient
import zlib
from server import app

client = TestClient(app)

def test_root_index():
    response = client.get("/")
    assert response.status_code == 200

def test_mission_coordinates_setup():
    payload = {
        "pad_lat": 14.7883,
        "pad_lon": -90.1988,
        "target_lat": 14.6133,
        "target_lon": -90.5283
    }
    response = client.post("/api/mission/coordinates", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "mission_id" in data

def test_orbit_plan_crc32_security():
    target_alt = 50.0
    payload_str = f"{target_alt:.1f}"
    valid_crc = zlib.crc32(payload_str.encode('utf-8')) & 0xFFFFFFFF

    # Prueba con CRC correcto
    response = client.post("/api/orbit/plan", json={"target_altitude_km": target_alt, "crc32_checksum": valid_crc})
    assert response.status_code == 200
    assert response.json()["status"] == "UPLINK_SECURE_ACCEPTED"

    # Prueba con CRC incorrecto (debe fallar por seguridad FSW)
    response_fail = client.post("/api/orbit/plan", json={"target_altitude_km": target_alt, "crc32_checksum": 12345678})
    assert response_fail.status_code == 400

def test_abort_sequence():
    response = client.post("/api/mission/abort")
    assert response.status_code == 200
    assert response.json()["status"] == "ABORT_SEQUENCE_ACTIVATED"
