import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_export_csv_endpoint():
    response = client.get("/export/csv")
    # Si hay datos devuelve CSV, si no hay registros activos devuelve JSON de error controlado
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    if "text/csv" in content_type:
        assert "Mission Time" in response.text
    else:
        assert "application/json" in content_type
        assert "error" in response.json()

def test_ai_query_endpoint():
    response = client.post("/ai/query", json={"prompt": "¿Cuál es el estado nominal de la misión?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data or "error" in data
