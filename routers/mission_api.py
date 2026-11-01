from fastapi import APIRouter, Request
from routers import mission_path
import os
import json

router = APIRouter(prefix="/api/mission", tags=["Mission API"])

fsw_state = {
    "time": 0,
    "altitude": 25.0,
    "velocity": 5.0,
    "lat": 14.7883,
    "lon": -90.1988,
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 0.0,
    "rw_momentum": 0.12,
    "active": False
}

@router.get("/status")
def get_mission_status():
    return {"status": "nominal", "fsw_state": fsw_state}

@router.post("/start")
async def start_mission(request: Request):
    fsw_state["active"] = True
    waypoints_to_load = []

    # 1. Intentar leer del cuerpo HTTP enviado por la UI
    try:
        body = await request.json()
        if isinstance(body, list):
            waypoints_to_load = body
        elif isinstance(body, dict):
            waypoints_to_load = body.get("waypoints", [])
    except Exception:
        pass

    # 2. Si no vinieron en el cuerpo, leer del archivo saved_mission.json
    if not waypoints_to_load and os.path.exists("saved_mission.json"):
        try:
            with open("saved_mission.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    waypoints_to_load = data
                elif isinstance(data, dict):
                    waypoints_to_load = data.get("waypoints", [])
        except Exception:
            pass

    # 3. Fallback si todo está vacío
    if not waypoints_to_load:
        waypoints_to_load = [
            {"lat": 14.7884, "lon": -90.1987, "alt": 35.0},
            {"lat": 14.7880, "lon": -90.1988, "alt": 35.0}
        ]

    # Asignación segura compatible con cualquier versión de MissionNavigator
    nav = mission_path.navigator
    if hasattr(nav, "load_waypoints"):
        nav.load_waypoints(waypoints_to_load)
    elif hasattr(nav, "set_waypoints"):
        nav.set_waypoints(waypoints_to_load)
    elif hasattr(nav, "waypoints"):
        nav.waypoints = waypoints_to_load
    
    # Asegurar activación del bucle de navegación
    if hasattr(nav, "is_active"):
        nav.is_active = True
    if hasattr(nav, "reset"):
        nav.reset()

    return {"status": "SUCCESS", "message": f"Misión iniciada con {len(waypoints_to_load)} waypoints."}

@router.post("/abort")
async def abort_mission():
    fsw_state["active"] = False
    if hasattr(mission_path.navigator, "is_active"):
        mission_path.navigator.is_active = False
    fsw_state["velocity"] = 0.0
    return {"status": "SUCCESS", "message": "Misión abortada / RTL forzado activado."}
