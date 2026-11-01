from fastapi import APIRouter
from routers import mission_api

router = APIRouter(prefix="/api/dji", tags=["DJI Bridge"])

@router.post("/telemetry")
async def receive_dji_telemetry(data: dict):
    """
    Recibe la telemetría simulada por la SDK comercial
    y la mapea al estado global de ODYSSEY-1.
    """
    mission_api.fsw_state["lat"] = data.get("latitude", 14.7883)
    mission_api.fsw_state["lon"] = data.get("longitude", -90.1988)
    mission_api.fsw_state["altitude"] = data.get("altitude_meters", 0.0)
    mission_api.fsw_state["velocity"] = data.get("speed_ms", 0.0)
    mission_api.fsw_state["pitch"] = data.get("pitch", 0.0)
    mission_api.fsw_state["roll"] = data.get("roll", 0.0)
    mission_api.fsw_state["yaw"] = data.get("yaw", 0.0)
    
    return {"status": "synced", "source": "DJI_SDK_SIMULATOR"}
