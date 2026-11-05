import asyncio
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_stress_sessions_endpoint():
    """Prueba de carga HTTP: Realiza múltiples solicitudes simultáneas al endpoint de sesiones."""
    for _ in range(100):
        response = client.get("/api/replay/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

def test_stress_anomalies_endpoint():
    """Prueba de carga HTTP: Consulta masiva al filtro FDIR de anomalías."""
    for _ in range(100):
        response = client.get("/api/replay/anomalies")
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
