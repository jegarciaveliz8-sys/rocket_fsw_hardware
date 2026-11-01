from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/mission", tags=["Mission"])

# Estado inicial del FSW centrado en Sanarate
fsw_state: Dict[str, Any] = {
    "time": 0,
    "altitude": 0.0,
    "velocity": 0.0,
    "chamber_pressure": 15.4,
    "battery_pct": 100.0,
    "lat": 14.7883,  # Base Sanarate Latitud
    "lon": -90.1988, # Base Sanarate Longitud
    "rw_momentum": 0.0,
    "status": "STANDBY / READY"
}

class WaypointModel(BaseModel):
    lat: float
    lon: float
    alt: float = 35.0
    loiter: int = 5
    name: str = "Waypoint"

class MissionRequest(BaseModel):
    waypoints: List[WaypointModel]

@router.post("/start")
async def start_mission(data: MissionRequest):
    from routers.mission_path import navigator
    wps = [wp.dict() for wp in data.waypoints]
    navigator.load_waypoints(wps)
    fsw_state["status"] = "MISSION ACTIVE"
    return {"status": "SUCCESS", "message": f"Misión iniciada con {len(wps)} waypoints en Sanarate."}

@router.post("/abort")
async def abort_mission():
    from routers.mission_path import navigator
    navigator.is_active = False
    fsw_state["status"] = "ABORTED / RTL"
    return {"status": "SUCCESS", "message": "Misión abortada. Modo RTL activado."}
