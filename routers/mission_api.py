from fastapi import APIRouter

router = APIRouter(prefix="/api/mission", tags=["Mission API"])

# Estado global del FSW (Flight Software) inicializado en Sanarate, Guatemala
fsw_state = {
    "time": 0,
    "altitude": 25.0,        # Altitud inicial en metros (vuelo bajo nominal)
    "velocity": 5.0,         # Velocidad en m/s
    "lat": 14.7883,          # Latitud Sanarate
    "lon": -90.1988,         # Longitud Sanarate
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 0.0,
    "rw_momentum": 0.12
}

@router.get("/status")
def get_mission_status():
    return {"status": "nominal", "fsw_state": fsw_state}
