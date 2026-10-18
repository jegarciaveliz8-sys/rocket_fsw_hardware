import os
import asyncio
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import physics_engine
from ukf_filter import RocketUKF
from fdir_engine import FDIRSystem
import ccsds_crypto
import ai_copilot

app = FastAPI(title="ODYSSEY-1 Mission Control Center")

# Instancias globales
ukf = RocketUKF()
fdir = FDIRSystem()

# Estado inicial del cohete [x, y, z, vx, vy, vz]
# x = R_earth + 400km (Órbita LEO), vy = ~7.67 km/s
state_real = np.array([6778137.0, 0.0, 0.0, 0.0, 7670.0, 0.0])
mass = 50000.0  # kg
cd = 0.3
area = 10.0     # m^2

# Servir archivos estáticos si existen
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
        "falla_fdir": fdir.injected_fault
    }
    
    response = ai_copilot.ask_flight_director_ai(state_summary, data.query)
    return {"response": response}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global state_real
    await websocket.accept()
    dt = 1.0  # Paso de tiempo de simulación (1s)
    
    try:
        while True:
            pos = state_real[:3]
            vel = state_real[3:]
            
            # 1. Calcular aceleraciones físicas reales (Gravedad + J2 + Arrastre)
            acc = physics_engine.calculate_accelerations(pos, vel, mass, cd, area)
            
            # Integración numérica de Euler para posición y velocidad
            vel = vel + acc * dt
            pos = pos + vel * dt
            state_real = np.hstack([pos, vel])
            
            # 2. Estimación de navegación UKF
            ukf.predict(dt)
            # Simular medición de posición con un pequeño ruido
            z_measured = pos + np.random.normal(0, 5.0, 3)
            ukf.update(z_measured)
            state_estimated = ukf.x
            
            # 3. Evaluación FDIR (Residuos entre real y modelo/estimación)
            fdir_msg = fdir.evaluate_telemetry(state_real, state_estimated)
            
            # 4. Construcción de trama binaria CCSDS
            alt_m = np.linalg.norm(pos) - 6378137.0
            speed_ms = np.linalg.norm(vel)
            
            payload_str = f"ALT:{alt_m:.1f};VEL:{speed_ms:.1f};FDIR:{fdir.status}"
            payload_bytes = payload_str.encode('utf-8')
            
            ccsds_frame = ccsds_crypto.build_ccsds_frame(apid=0x01A, data_payload=payload_bytes)
            is_valid_crc = ccsds_crypto.verify_ccsds_frame(ccsds_frame)
            
            # 5. Enviar paquete JSON al cliente Web
            telemetry_data = {
                "altitude_km": round(alt_m / 1000.0, 2),
                "speed_kmh": round((speed_ms * 3600.0) / 1000.0, 2),
                "position_xyz": [round(p, 1) for p in pos],
                "velocity_xyz": [round(v, 1) for v in vel],
                "ukf_estimated_xyz": [round(p, 1) for p in state_estimated[:3]],
                "fdir_status": fdir.status,
                "fdir_fault": fdir.injected_fault,
                "fdir_action": fdir_msg,
                "ccsds_hex": ccsds_frame.hex().upper()[:32] + "...",
                "ccsds_crc_valid": is_valid_crc
            }
            
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        pass
