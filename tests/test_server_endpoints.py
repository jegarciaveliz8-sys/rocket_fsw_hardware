from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_get_ui_info():
    response = client.get("/ui")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.3.0"
    assert data["system"] == "ODYSSEY-1 GCS"

def test_orbit_panel_accessibility():
    response = client.get("/orbit")
    assert response.status_code == 200
    assert "<html" in response.text.lower()
