import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_root_or_docs():
    # Verifica que FastAPI responda correctamente en la documentación o rutas básicas
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_websocket_lifecycle():
    with client.websocket_connect("/ws/telemetry") as websocket:
        # Enviar comando de lanzamiento
        websocket.send_json({"command": "LAUNCH"})
        # Recibir respuesta de telemetría del servidor
        data = websocket.receive_json()
        assert "altitude" in data
        assert "velocity" in data
        assert data["status"] == "POWERED ASCENT"
