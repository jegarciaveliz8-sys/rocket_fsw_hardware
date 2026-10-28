from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_dvr_lifecycle():
    # Iniciar DVR
    res_start = client.post("/api/dvr/start")
    assert res_start.status_code == 200
    assert res_start.json()["dvr_state"] == "RECORDING"

    # Listar sesiones
    res_list = client.get("/api/dvr/sessions")
    assert res_list.status_code == 200
    assert len(res_list.json()["sessions"]) > 0

    # Detener DVR
    res_stop = client.post("/api/dvr/stop")
    assert res_stop.status_code == 200
    assert res_stop.json()["dvr_state"] == "STOPPED"

def test_pdf_report_generation():
    response = client.get("/api/reports/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert b"%PDF" in response.content

def test_flight_vectors():
    response = client.get("/api/reports/vectors")
    assert response.status_code == 200
    data = response.json()
    assert "position_vector" in data
    assert "velocity_vector" in data
    assert "heading_degrees" in data
