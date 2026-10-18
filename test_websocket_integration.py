import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_websocket_launch_flow():
    with client.websocket_connect("/ws/telemetry") as websocket:
        # Enviar comando de lanzamiento al servidor
        websocket.send_json({"command": "LAUNCH"})
        
        # Recibir la primera trama de telemetría procesada por el servidor y el EKF
        data = websocket.receive_json()
        
        # Verificar que la estructura y el estado sean los correctos
        assert "altitude" in data
        assert "velocity" in data
        assert "status" in data
        assert data["status"] == "POWERED ASCENT"
        assert isinstance(data["altitude"], float)
        assert isinstance(data["velocity"], float)
