import os
import asyncio
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import physics_engine
from ukf_filter import RocketUKF
from fdir_engine import FDIRSystem
import ccsds_crypto
import ai_copilot

app = FastAPI(title="ODYSSEY-1 Mission Control Center")

ukf = RocketUKF()
fdir = FDIRSystem()

state_real = np.array([6778137.0, 0.0, 0.0, 0.0, 7670.0, 0.0])
mass = 50000.0
cd = 0.3
area = 10.0

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ODYSSEY-1 Mission Control Center Backend Operational</h1>"

class AIQuery(BaseModel):
    query: str

@app.post("/api/ai/ask")
async def ask_ai(data: AIQuery):
    pos = state_real[:3]
    vel = state_real[3:]
    alt_km = (np.linalg.norm(pos) - 6378137.0) / 1000.0
    speed_kms = np.linalg.norm(vel) / 1000.0
    
    state_summary = {
        "altitud_km": round(alt_km, 2),
        "velocidad_kms": round(speed_kms, 2),
        "estado_fdir": fdir.status,
        "falla_fdir": fdir.injected_fault,
        "matriz_subsistemas": fdir.subsystems,
        "sdls_status": "AUTHENTICATED_VALID"
    }
    
    response = ai_copilot.ask_flight_director_ai(state_summary, data.query)
    return {"response": response}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global state_real
    await websocket.accept()
    dt = 1.0
    
    ukf.initialize(state_real)
    
    try:
        while True:
            pos = state_real[:3]
            vel = state_real[3:]
            
            # 1. Física espacial con J2 y Arrastre
            acc = physics_engine.calculate_accelerations(pos, vel, mass, cd, area)
            vel = vel + acc * dt
            pos = pos + vel * dt
            state_real = np.hstack([pos, vel])
            
            # 2. Navegación UKF
            ukf.predict(dt, imu_acceleration=acc)
            gps_measured = pos + np.random.normal(0, 8.0, 3)
            ukf.update(gps_measured)
            state_estimated = ukf.x
            
            # 3. FDIR Autónomo
            fdir_action = fdir.evaluate_telemetry(state_real, state_estimated)
            
            # 4. CCSDS / SDLS Security
            alt_m = np.linalg.norm(pos) - 6378137.0
            speed_ms = np.linalg.norm(vel)
            payload_str = f"ALT:{alt_m:.1f};VEL:{speed_ms:.1f};FDIR:{fdir.status}"
            
            ccsds_frame = ccsds_crypto.build_ccsds_frame(apid=0x01A, data_payload=payload_str.encode('utf-8'))
            security_check = ccsds_crypto.verify_ccsds_frame(ccsds_frame)
            
            telemetry_data = {
                "altitude_km": round(alt_m / 1000.0, 2),
                "speed_kmh": round((speed_ms * 3600.0) / 1000.0, 2),
                "position_xyz": [round(p, 1) for p in pos],
                "velocity_xyz": [round(v, 1) for v in vel],
                "ukf_estimated_xyz": [round(p, 1) for p in state_estimated[:3]],
                "fdir_status": fdir.status,
                "fdir_fault": fdir.injected_fault,
                "fdir_action": fdir_action,
                "fdir_subsystems": fdir.subsystems,
                "ccsds_hex": ccsds_frame.hex().upper()[:36] + "...",
                "ccsds_crc_valid": security_check["valid"],
                "sdls_status": security_check["error"]
            }
            
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        pass
