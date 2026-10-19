import os
import json
import asyncio
import math
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="ODYSSEY-1 Advanced Flight Software & MCC")

# Estado global del sistema de vuelo y simulador
mission_state = {
    "pad_lat": 14.7883,
    "pad_lon": -90.1988,
    "target_lat": 14.6133,
    "target_lon": -90.5283,
    "target_altitude_km": 50.0,
    "altitude_km": 0.0,
    "speed_kmh": 0.0,
    "sequencer_state": "STANDBY_LAUNCH_PAD",
    "active_soi": "EARTH_ATMOSPHERIC_TACTICAL",
    "dsn_station": "Guatemala Tactical Link",
    "mahalanobis_d2": 0.02,
    "hil_mode": "VIRTUAL_SIMULATION",
    "abort_triggered": False,
    "hardware_telemetry": None
}

class MissionCoordinates(BaseModel):
    pad_lat: float
    pad_lon: float
    target_lat: float
    target_lon: float

class OrbitPlanRequest(BaseModel):
    target_altitude_km: float

class HardwareTelemetryInput(BaseModel):
    device_id: str
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float
    pitch: float
    roll: float
    yaw: float
    alt_msl: float

@app.post("/api/mission/coordinates")
async def set_coordinates(coords: MissionCoordinates):
    mission_state["pad_lat"] = coords.pad_lat
    mission_state["pad_lon"] = coords.pad_lon
    mission_state["target_lat"] = coords.target_lat
    mission_state["target_lon"] = coords.target_lon
    mission_state["sequencer_state"] = "COORDINATES_LOCKED"
    return {"status": "success", "updated_coordinates": coords.dict()}

@app.post("/api/mission/abort")
async def trigger_abort():
    """Opción 3: Disparador de Aborto y Terminación de Vuelo (FSM)"""
    mission_state["abort_triggered"] = True
    mission_state["sequencer_state"] = "ABORT_MISSION_LES_TRIGGERED"
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "action": "THRUST_TERMINATION"}

@app.post("/api/hardware/telemetry")
async def receive_hardware_telemetry(data: HardwareTelemetryInput):
    """Opción 2: Endpoint para recibir datos de placas físicas (HIL - ESP32 / Arduino / RPi)"""
    mission_state["hil_mode"] = f"HARDWARE_LINKED ({data.device_id})"
    mission_state["hardware_telemetry"] = data.dict()
    mission_state["altitude_km"] = round(data.alt_msl / 1000.0, 3)
    return {"status": "telemetry_ingested"}

@app.post("/api/orbit/plan")
async def plan_orbit(req: OrbitPlanRequest):
    mission_state["target_altitude_km"] = req.target_altitude_km
    mission_state["sequencer_state"] = "POWERED_FLIGHT_PROPULSION"
    return {
        "burn_plan": {
            "dv_magnitude_m_s": round(math.sqrt(req.target_altitude_km * 9.81 * 1000) * 0.1, 2),
            "target_altitude_km": req.target_altitude_km
        }
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    t = 0.0
    dt = 0.02
    
    try:
        while True:
            t += dt
            
            # Opción 1: Ecuaciones de Propagación Balística Real
            if not mission_state["abort_triggered"]:
                progress = (math.sin(t * 0.5) + 1.0) / 2.0  # Progresión de trayectoria
                
                # Cálculo geodésico
                current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * progress
                current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * progress
                
                # Perfil de altitud balística (parábola)
                max_alt = mission_state["target_altitude_km"]
                current_alt = max_alt * 4.0 * progress * (1.0 - progress)
                
                # Cálculo de velocidad balística
                v_horizontal = 1200.0  # km/h
                v_vertical = (1.0 - 2.0 * progress) * 1800.0
                total_speed = round(math.sqrt(v_horizontal**2 + v_vertical**2), 1)
                
                if mission_state["sequencer_state"] not in ["COORDINATES_LOCKED", "STANDBY_LAUNCH_PAD"]:
                    mission_state["sequencer_state"] = "BALISTIC_MIDCOURSE_GUIDANCE" if progress < 0.8 else "TERMINAL_HOMING"
            else:
                # Comportamiento ante Aborto (Caída balística no controlada)
                current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * 0.4
                current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * 0.4
                current_alt = max(0.0, mission_state["altitude_km"] - 1.5)
                total_speed = round(current_alt * 250.0, 1)

            mission_state["altitude_km"] = round(current_alt, 3)
            mission_state["speed_kmh"] = total_speed

            telemetry_payload = {
                "altitude_km": mission_state["altitude_km"],
                "speed_kmh": mission_state["speed_kmh"],
                "active_soi": mission_state["active_soi"],
                "sequencer_state": mission_state["sequencer_state"],
                "dsn_station": mission_state["dsn_station"],
                "mahalanobis_d2": round(0.02 + math.sin(t) * 0.01, 2),
                "hil_mode": mission_state["hil_mode"],
                "geodetic": {
                    "lat": round(current_lat, 5),
                    "lon": round(current_lon, 5),
                    "alt": round(current_alt * 1000.0, 1)
                }
            }
            
            await websocket.send_text(json.dumps(telemetry_payload))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

app.mount("/", StaticFiles(directory="static", html=True), name="static")
