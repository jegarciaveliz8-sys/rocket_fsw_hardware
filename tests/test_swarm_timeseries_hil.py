from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_swarm_fleet_and_commands():
    res_fleet = client.get("/api/swarm/vehicles")
    assert res_fleet.status_code == 200
    assert res_fleet.json()["fleet_size"] == 3

    res_cmd = client.post("/api/swarm/command", json={"command": "RTL"})
    assert res_cmd.status_code == 200
    assert res_cmd.json()["broadcast_command"] == "RTL"

def test_timeseries_database_query():
    response = client.get("/api/timeseries/query?metric=altitude&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "altitude"
    assert len(data["data_points"]) == 5

def test_hardware_in_the_loop_simulation():
    res_conn = client.post("/api/hil/connect", json={"interface": "USB_UART_1", "baudrate": 921600})
    assert res_conn.status_code == 200
    assert res_conn.json()["hil_state"] == "CONNECTED"

    res_status = client.get("/api/hil/status")
    assert res_status.status_code == 200
    assert res_status.json()["hardware_in_loop"] is True
