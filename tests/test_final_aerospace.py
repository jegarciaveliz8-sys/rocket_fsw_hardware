from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_video_feeds_and_ptz():
    res_streams = client.get("/api/video/streams")
    assert res_streams.status_code == 200
    assert len(res_streams.json()["streams"]) > 0

    res_ptz = client.post("/api/video/ptz", json={"pan": 15.5, "tilt": -5.0, "zoom": 2.0})
    assert res_ptz.status_code == 200
    assert res_ptz.json()["zoom"] == 2.0

def test_timeline_countdown():
    res_status = client.get("/api/timeline/status")
    assert res_status.status_code == 200
    assert "countdown_state" in res_status.json()

    res_hold = client.post("/api/timeline/hold")
    assert res_hold.status_code == 200
    assert res_hold.json()["countdown_state"] == "HOLD"

def test_weather_wind_profile():
    response = client.get("/api/weather/profile")
    assert response.status_code == 200
    data = response.json()
    assert "altitude_wind_layers" in data
    assert len(data["altitude_wind_layers"]) > 0

def test_replay_scrubber():
    response = client.post("/api/replay/seek", json={"timestamp": 1793149950, "speed": 5.0})
    assert response.status_code == 200
    data = response.json()
    assert data["playback_speed"] == "5.0x"
    assert data["current_seek_timestamp"] == 1793149950
