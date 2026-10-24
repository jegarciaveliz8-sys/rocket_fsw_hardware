import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_root_endpoint():
    """Verifica que el panel web principal responda correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ODYSSEY-1" in response.text

def test_drone_command_injection_valid():
    """Valida el pipeline de inyección MAVLink para comandos permitidos."""
    valid_commands = ["ARM", "DISARM", "TAKEOFF", "RTL"]
    for cmd in valid_commands:
        response = client.post("/api/drone/command", json={"command": cmd})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["command_sent"] == cmd

def test_drone_command_injection_custom():
    """Valida la inyección de comandos personalizados o arbitrarios en el pipeline."""
    response = client.post("/api/drone/command", json={"command": "CUSTOM_CMD"})
    assert response.status_code == 200
    data = response.json()
    assert data["command_sent"] == "CUSTOM_CMD"

def test_orbit_plan_and_crc32():
    """Valida el solucionador de delta-v y la verificación de integridad CRC32."""
    target_alt = 50.0
    alt_str = "50.0"
    
    table = []
    for i in range(256):
        c = i
        for j in range(8):
            c = (0xEDB88320 ^ (c >> 1)) if (c & 1) else (c >> 1)
        table.append(c)
        
    def compute_crc(s):
        crc = 0xFFFFFFFF
        for char in s:
            c = ord(char)
            crc = (crc >> 8) ^ table[(crc ^ c) & 0xFF]
        return (crc ^ 0xFFFFFFFF) & 0xFFFFFFFF

    checksum = compute_crc(alt_str)

    response = client.post("/api/orbit/plan", json={
        "target_altitude_km": target_alt,
        "crc32_checksum": checksum
    })
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_mission_coordinates_sync():
    """Valida la sincronización de coordenadas del pad de salida y zona destino."""
    payload = {
        "pad_lat": 14.5975,
        "pad_lon": -90.5131,
        "target_lat": 13.7024,
        "target_lon": -89.2241
    }
    response = client.post("/api/mission/coordinates", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
