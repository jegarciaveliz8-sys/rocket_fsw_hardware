from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_get_recorded_sessions():
    response = client.get("/api/replay/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "frames" in data
    assert "total_frames" in data

def test_get_mission_anomalies():
    response = client.get("/api/replay/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data

def test_export_csv_report():
    response = client.get("/api/replay/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "odyssey_flight_audit_report.csv" in response.headers["content-disposition"]
