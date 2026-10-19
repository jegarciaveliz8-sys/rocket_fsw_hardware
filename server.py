import os
import json
import asyncio
import math
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="ODYSSEY-1 Flight Software & Control Center")

# Estado global simulado de la misión
mission_state = {
    "pad_lat": 28.572,
    "pad_lon": -80.604,
    "target_lat": 30.0,
    "target_lon": 15.0,
    "target_altitude_km": 500.0,
    "altitude_km": 399.5,
    "speed_kmh": 27400.0,
    "sequencer_state": "ORBITAL_PROPAGATION",
    "active_soi": "EARTH_GEO_LEO_SOI (TERRESTRIAL_DOMINANT)",
    "dsn_station": "Madrid (Spain)",
    "mahalanobis_d2": 0.09,
    "hil_mode": "VIRTUAL_SIMULATION"
}

class MissionCoordinates(BaseModel):
    pad_lat: float
    pad_lon: float
    target_lat: float
    target_lon: float

class OrbitPlanRequest(BaseModel):
    target_altitude_km: float

class AIQueryRequest(BaseModel):
    query: str

@app.post("/api/mission/coordinates")
async def set_coordinates(coords: MissionCoordinates):
    mission_state["pad_lat"] = coords.pad_lat
    mission_state["pad_lon"] = coords.pad_lon
    mission_state["target_lat"] = coords.target_lat
    mission_state["target_lon"] = coords.target_lon
    return {
        "status": "success",
        "message": "Coordenadas de misión actualizadas en el servidor backend.",
        "updated_coordinates": coords.dict()
    }

@app.post("/api/orbit/plan")
async def plan_orbit(req: OrbitPlanRequest):
    # Cálculo elemental de manobra delta-v basado en altitud
    alt_diff = req.target_altitude_km - mission_state["altitude_km"]
    dv = math.sqrt(abs(alt_diff)) * 10.3
    burn_plan = {
        "dv_magnitude_m_s": round(dv, 3),
        "dv_vector_xyz": [round(-dv * 0.075, 3), round(dv * 0.997, 3), 0.0],
        "target_semi_major_axis_km": round(6371.0 + req.target_altitude_km, 3)
    }
    return {
        "burn_plan": burn_plan,
        "keplerian_elements": {
            "semi_major_axis_km": round(6371.0 + mission_state["altitude_km"], 3),
            "eccentricity": 0.012368,
            "inclination_deg": 0.0
        }
    }

@app.post("/api/ai/ask")
async def ask_copilot(req: AIQueryRequest):
    return {
        "response": f"Analizando consulta de vuelo: '{req.query}'. Telemetría nominal. Altitud actual: {mission_state['altitude_km']} km."
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    step = 0
    try:
        while True:
            step += 0.01
            # Simulación dinámica de avance lat/lon
            current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * (math.sin(step) * 0.5 + 0.5)
            current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * (math.sin(step) * 0.5 + 0.5)
            
            telemetry_payload = {
                "altitude_km": round(mission_state["altitude_km"] + math.sin(step) * 2.0, 3),
                "speed_kmh": round(mission_state["speed_kmh"] + math.cos(step) * 15.0, 1),
                "active_soi": mission_state["active_soi"],
                "sequencer_state": mission_state["sequencer_state"],
                "dsn_station": mission_state["dsn_station"],
                "mahalanobis_d2": round(mission_state["mahalanobis_d2"] + math.sin(step) * 0.01, 2),
                "hil_mode": mission_state["hil_mode"],
                "geodetic": {
                    "lat": round(current_lat, 4),
                    "lon": round(current_lon, 4),
                    "alt": round(mission_state["altitude_km"] * 1000.0, 1)
                }
            }
            await websocket.send_text(json.dumps(telemetry_payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

app.mount("/", StaticFiles(directory="static", html=True), name="static")
