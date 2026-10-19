import os
import json
import asyncio
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="ODYSSEY-1 Advanced Flight Software & MCC")

mission_state = {
    "pad_lat": 14.7883,
    "pad_lon": -90.1988,
    "target_lat": 14.6133,
    "target_lon": -90.5283,
    "target_altitude_km": 50.0,
    "altitude_km": 0.0,
    "speed_kmh": 0.0,
    "sequencer_state": "POWERED_FLIGHT_PROPULSION",
    "active_soi": "EARTH_ATMOSPHERIC_TACTICAL",
    "dsn_station": "Guatemala Tactical Link",
    "hil_mode": "VIRTUAL_SIMULATION",
    "abort_triggered": False,
    "flight_time": 0.0
}

class MissionCoordinates(BaseModel):
    pad_lat: float
    pad_lon: float
    target_lat: float
    target_lon: float

class OrbitPlanRequest(BaseModel):
    target_altitude_km: float

@app.post("/api/mission/coordinates")
async def set_coordinates(coords: MissionCoordinates):
    mission_state["pad_lat"] = coords.pad_lat
    mission_state["pad_lon"] = coords.pad_lon
    mission_state["target_lat"] = coords.target_lat
    mission_state["target_lon"] = coords.target_lon
    mission_state["sequencer_state"] = "POWERED_FLIGHT_PROPULSION"
    mission_state["abort_triggered"] = False
    mission_state["flight_time"] = 0.0
    return {"status": "success", "updated_coordinates": coords.dict()}

@app.post("/api/mission/abort")
async def trigger_abort():
    mission_state["abort_triggered"] = True
    mission_state["sequencer_state"] = "ABORT_MISSION_LES_TRIGGERED"
    return {"status": "ABORT_SEQUENCE_ACTIVATED"}

@app.post("/api/orbit/plan")
async def plan_orbit(req: OrbitPlanRequest):
    mission_state["target_altitude_km"] = req.target_altitude_km
    return {
        "burn_plan": {
            "dv_magnitude_m_s": round(math.sqrt(req.target_altitude_km * 9.81 * 1000) * 0.1, 2),
            "target_altitude_km": req.target_altitude_km
        }
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    dt = 0.1
    
    try:
        while True:
            if not mission_state["abort_triggered"]:
                mission_state["flight_time"] += dt
                # Duración total del vuelo: ~30 segundos para completar el trayecto
                total_duration = 30.0
                progress = min(mission_state["flight_time"] / total_duration, 1.0)
                
                current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * progress
                current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * progress
                
                max_alt = mission_state["target_altitude_km"]
                # Parábola balística que sube y baja hasta el impacto (progress = 1.0 -> alt = 0)
                current_alt = max_alt * 4.0 * progress * (1.0 - progress) if progress < 1.0 else 0.0
                
                if progress >= 1.0:
                    fsm_status = "MISSION_COMPLETED_IMPACT_SUCCESS"
                    total_speed = 0.0
                elif progress > 0.85:
                    fsm_status = "TERMINAL_HOMING_DESCENT"
                    total_speed = 450.0
                else:
                    fsm_status = "BALISTIC_MIDCOURSE_GUIDANCE"
                    total_speed = 2400.0
                    
                mission_state["sequencer_state"] = fsm_status
            else:
                current_lat = mission_state["target_lat"]
                current_lon = mission_state["target_lon"]
                current_alt = 0.0
                total_speed = 0.0

            mission_state["altitude_km"] = round(current_alt, 2)
            mission_state["speed_kmh"] = total_speed

            telemetry_payload = {
                "altitude_km": mission_state["altitude_km"],
                "speed_kmh": mission_state["speed_kmh"],
                "active_soi": mission_state["active_soi"],
                "sequencer_state": mission_state["sequencer_state"],
                "dsn_station": mission_state["dsn_station"],
                "hil_mode": mission_state["hil_mode"],
                "geodetic": {
                    "lat": round(current_lat, 5),
                    "lon": round(current_lon, 5),
                    "alt": round(current_alt * 1000.0, 1)
                }
            }
            
            await websocket.send_text(json.dumps(telemetry_payload))
            await asyncio.sleep(0.3)
    except WebSocketDisconnect:
        pass

app.mount("/", StaticFiles(directory="static", html=True), name="static")
