from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

router = APIRouter(prefix="/api/mission-planner", tags=["Mission Planner"])
MISSION_FILE = "saved_mission.json"

class MissionPayload(BaseModel):
    waypoints: list

@router.post("/save")
async def save_mission(payload: MissionPayload):
    try:
        with open(MISSION_FILE, "w", encoding="utf-8") as f:
            json.dump(payload.waypoints, f, indent=4)
        return {"status": "SUCCESS", "message": "Misión guardada en servidor correctamente"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@router.get("/load")
async def load_mission():
    if not os.path.exists(MISSION_FILE):
        return {"status": "ERROR", "message": "No hay misiones guardadas"}
    try:
        with open(MISSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"status": "SUCCESS", "waypoints": data}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
