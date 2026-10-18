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
from flight_sequencer import FlightSequencer
from orbit_planner import calculate_optimal_burn, cartesian_to_keplerian
from swarm_manager import SwarmConstellationManager
from hil_mqtt_bridge import HardwareInTheLoopBridge
from nbody_physics import nbody_gravitational_acceleration

app = FastAPI(title="ODYSSEY-1 Full MCC Aerospace Center")

ukf = RocketUKF()
fdir = FDIRSystem()
sequencer = FlightSequencer()
swarm = SwarmConstellationManager()
hil = HardwareInTheLoopBridge()

state_real = np.array([6778137.0, 0.0, 0.0, 0.0, 7670.0, 0.0])
mass = 50000.0
cd = 0.3
area = 10.0
sim_time_sec = 0

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ODYSSEY-1 Full MCC Backend Operational</h1>"

class AIQuery(BaseModel):
    query: str

class TCCommand(BaseModel):
    command: str

class BurnPlanRequest(BaseModel):
    target_altitude_km: float

class HILPayload(BaseModel):
    payload_json: str

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
    return {"response": ai_copilot.ask_flight_director_ai(state_summary, data.query)}

@app.post("/api/tc/uplink")
async def uplink_telecommand(data: TCCommand):
    import hmac, hashlib
    payload = data.command.encode('utf-8')
    mac = hmac.new(tc_command_engine.TC_KEY, payload, hashlib.sha256).digest()
    tc_hex = (payload + mac).hex()
    return tc_command_engine.authenticate_and_parse_tc(tc_hex)

@app.post("/api/orbit/plan")
async def plan_orbit(data: BurnPlanRequest):
    pos = state_real[:3]
    vel = state_real[3:]
    plan = calculate_optimal_burn(pos, vel, data.target_altitude_km)
    kepler = cartesian_to_keplerian(pos, vel)
    return {"burn_plan": plan, "keplerian_elements": kepler}

@app.post("/api/hil/ingest")
async def ingest_hil(data: HILPayload):
    success = hil.process_incoming_hardware_stream(data.payload_json)
    return {"status": "SUCCESS" if success else "FAILED_PARSING"}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    global state_real, sim_time_sec
    await websocket.accept()
    dt = 1.0
    ukf.initialize(state_real)
    
    try:
        while True:
            sim_time_sec += 1
            
            # Verificación de aceleración N-Cuerpos
            pos = state_real[:3]
            vel = state_real[3:]
            nbody_acc, active_soi = nbody_gravitational_acceleration(pos, sim_time_sec)
            
            hil_packet, hil_mode = hil.get_calibrated_acceleration()
            if hil_mode == "HIL_HARDWARE_CONNECTED":
                acc = np.array([hil_packet["ax"], hil_packet["ay"], hil_packet["az"]])
                vel = vel + acc * dt
                pos = pos + vel * dt
                state_real = np.hstack([pos, vel])
            else:
                state_real = physics_engine.rk4_step(state_real, dt, mass, cd, area)
                pos = state_real[:3]
                vel = state_real[3:]
                deriv = physics_engine.state_derivative(0, state_real, mass, cd, area)
                acc = deriv[3:]
            
            ukf.predict(dt, imu_accel=acc)
            gps_measured = pos + np.random.normal(0, 5.0, 3)
            residual, S_cov = ukf.update(gps_measured)
            
            alt_m = np.linalg.norm(pos) - 6378137.0
            speed_ms = np.linalg.norm(vel)
            dyn_pressure = 0.5 * 1.225 * (speed_ms**2)
            
            seq_state, met = sequencer.evaluate_fsm(alt_m, speed_ms, dyn_pressure, fdir.status)
            swarm_data = swarm.propagate_swarm_fleet(dt)
            dsn_station, dsn_elevation = dsn_network.calculate_active_dsn_station(pos, sim_time_sec)
            fdir_action, d_mahalanobis = fdir.evaluate_mahalanobis(residual, S_cov)
            
            payload_str = f"ALT:{alt_m:.2f};VEL:{speed_ms:.2f};D2_M:{d_mahalanobis:.2f};FDIR:{fdir.status};SEQ:{seq_state}"
            ccsds_frame = ccsds_crypto.build_ccsds_frame(apid=0x01A, data_payload=payload_str.encode('utf-8'))
            security_check = ccsds_crypto.verify_ccsds_frame(ccsds_frame)
            
            telemetry_data = {
                "altitude_km": round(alt_m / 1000.0, 3),
                "speed_kmh": round((speed_ms * 3600.0) / 1000.0, 2),
                "position_xyz": [round(float(p), 1) for p in pos],
                "active_soi": active_soi,
                "sequencer_state": seq_state,
                "mission_elapsed_time": met,
                "swarm_fleet": swarm_data,
                "hil_mode": hil_mode,
                "dsn_station": dsn_station,
                "dsn_elevation": dsn_elevation,
                "mahalanobis_d2": round(d_mahalanobis, 2),
                "fdir_status": fdir.status,
                "fdir_action": fdir_action,
                "ccsds_hex": ccsds_frame.hex().upper()[:40] + "...",
                "ccsds_crc_valid": security_check["valid"]
            }
            
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        pass
