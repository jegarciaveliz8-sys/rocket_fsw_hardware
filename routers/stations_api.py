from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random

router = APIRouter(prefix="/api/dsn", tags=["Multi-Station Broker"])

stations_state = {
    "DSS-63": {"name": "Madrid (DSS-63) [MODULAR HIL]", "lat": 40.4295, "lon": -4.2458, "status": "ACTIVE", "frequency": "8.42 GHz", "snr": 18.4},
    "DSS-14": {"name": "Goldstone (DSS-14)", "lat": 35.4267, "lon": -116.8890, "status": "STANDBY", "frequency": "8.45 GHz", "snr": 16.2},
    "DSS-43": {"name": "Canberra (DSS-43)", "lat": -35.4014, "lon": 148.9817, "status": "STANDBY", "frequency": "8.41 GHz", "snr": 14.9}
}
active_station_id = "DSS-63"

class StationSwitchRequest(BaseModel):
    station: str = None
    station_id: str = None

@router.get("/")
async def list_stations():
    return {"active_station": active_station_id, "stations": stations_state}

@router.post("/switch")
async def switch_station(req: StationSwitchRequest):
    global active_station_id
    target = req.station or req.station_id
    if target in stations_state:
        for s in stations_state:
            stations_state[s]["status"] = "STANDBY"
        stations_state[target]["status"] = "ACTIVE"
        active_station_id = target
        st = stations_state[target]
        return {
            "status": "SUCCESS", 
            "name": st["name"],
            "active_station": st["name"],
            "lat": st["lat"],
            "lon": st["lon"]
        }
    raise HTTPException(status_code=404, detail="Estación DSN no encontrada.")

def get_active_station_telemetry():
    active_info = stations_state[active_station_id]
    return {
        "dsn_station": active_info["name"],
        "dsn_lat": active_info["lat"],
        "dsn_lon": active_info["lon"],
        "snr": round(active_info["snr"] + random.uniform(-0.3, 0.3), 1),
        "stations_status": stations_state
    }
