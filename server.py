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
import tc_command_engine
import dsn_network

app = FastAPI(title="ODYSSEY-1 Mission Control Center - Full MCC System")

ukf = RocketUKF()
fdir = FDIRSystem()

# Estado inicial ECI: 400km LEO orbit, v = 7.67 km/s
state_real = np.array([6778137.0, 0.0, 0.0, 0.0, 7670.0, 0.0])
mass = 50000.0  # kg
cd = 0.3
area = 10.0     # m^2
sim_time_sec = 0

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ODYSSEY-1 Advanced MCC Backend Operational</h1>"

class AIQuery(BaseModel):
    query: str

class TCCommand(BaseModel):
    command: str

@app.post("/api/ai/ask")
async def ask_ai(data: AIQuery):
    pos = state_real[:3]
    vel = state_real[3:]
    alt_km = (np.linalg.norm(pos) - 6378137.0) / 1000.0
    speed_kms = np.linalg.norm(vel) / 1000.0
    
    active_dsn, dsn_elev = dsn_network.calculate_active_dsn_station(pos, sim_time_sec)
    
    state_summary = {
        "altitud_km": round(alt_km, 3),
        "velocidad_kms": round(speed_kms, 3),
        "estacion_dsn": active_dsn,
        "elevacion_dsn": dsn_elev,
        "estado_fdir": fdir.status,
        "falla_fdir": fdir.injected_fault,
        "matriz_subsistemas": fdir.subsystems,
        "sdls_status": "AUTHENTICATED_RS255_223_VALID"
    }
    
    response = ai_copilot.ask_flight_director_ai(state_summary, data.query)
    return {"response": response}

@app.post("/api/tc/uplink")
async def uplink_telecommand(data: TCCommand):
    # Generar HMAC simulación
    import hmac, hashlib
    payload = data.command.encode('utf-8')
    mac = hmac.new(tc_command_engine.TC_KEY, payload, hashlib.sha256).digest()
    tc_hex = (payload + mac).hex()
    
    result = tc_command_engine.authenticate_and_parse_tc(tc_hex)
    return result

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global state_real, sim_time_sec
    await websocket.accept()
    dt = 1.0  # 1s sim step
    
    ukf.initialize(state_real)
    
    try:
        while True:
            sim_time_sec += 1
            
            # 1. Integración RK4 de la Física Espacial con J2, J3, Drag y SRP
            state_real = physics_engine.rk4_step(state_real, dt, mass, cd, area)
            pos = state_real[:3]
            vel = state_real[3:]
            
            # Aceleración real para IMU
            deriv = physics_engine.state_derivative(0, state_real, mass, cd, area)
            imu_accel = deriv[3:]
            
            # 2. Navegación Unscented Kalman Filter (9D)
            ukf.predict(dt, imu_accel=imu_accel)
            gps_measured = pos + np.random.normal(0, 5.0, 3)
            residual, S_cov = ukf.update(gps_measured)
            state_estimated = ukf.x[:6]
            
            # 3. DSN Station Tracking
            dsn_station, dsn_elevation = dsn_network.calculate_active_dsn_station(pos, sim_time_sec)
            
            # 4. FDIR con Distancia de Mahalanobis
            fdir_action, d_mahalanobis = fdir.evaluate_mahalanobis(residual, S_cov)
            
            # 5. Encriptación SDLS + Reed Solomon + CCSDS Frame
            alt_m = np.linalg.norm(pos) - 6378137.0
            speed_ms = np.linalg.norm(vel)
            payload_str = f"ALT:{alt_m:.2f};VEL:{speed_ms:.2f};D2_M:{d_mahalanobis:.2f};FDIR:{fdir.status}"
            
            ccsds_frame = ccsds_crypto.build_ccsds_frame(apid=0x01A, data_payload=payload_str.encode('utf-8'))
            security_check = ccsds_crypto.verify_ccsds_frame(ccsds_frame)
            
            telemetry_data = {
                "altitude_km": round(alt_m / 1000.0, 3),
                "speed_kmh": round((speed_ms * 3600.0) / 1000.0, 2),
                "position_xyz": [round(p, 2) for p in pos],
                "velocity_xyz": [round(v, 2) for v in vel],
                "ukf_estimated_xyz": [round(p, 2) for p in state_estimated[:3]],
                "dsn_station": dsn_station,
                "dsn_elevation": dsn_elevation,
                "mahalanobis_d2": round(d_mahalanobis, 2),
                "fdir_status": fdir.status,
                "fdir_fault": fdir.injected_fault,
                "fdir_action": fdir_action,
                "fdir_subsystems": fdir.subsystems,
                "ccsds_hex": ccsds_frame.hex().upper()[:40] + "...",
                "ccsds_crc_valid": security_check["valid"],
                "sdls_status": security_check["error"]
            }
            
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        pass
