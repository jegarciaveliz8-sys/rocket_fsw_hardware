from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import hashlib
import hmac

# Importación de routers existentes y el nuevo módulo de inyección de fallas
from routers import mission_api, subsystems_api, ai_copilot, dji_bridge, alerts_engine, blackbox, commands_api, mission_path, fault_injection

app = FastAPI(title="ODYSSEY-1 Modular Mission Control Center", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(BASE_DIR, "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir), name="web")

# Registro de routers
app.include_router(mission_api.router)
app.include_router(subsystems_api.router)
app.include_router(ai_copilot.router)
app.include_router(dji_bridge.router)
app.include_router(commands_api.router)
app.include_router(fault_injection.router) # <- Router de Inyección de Fallas integrado

@app.get("/")
def read_root():
    return {"system": "ODYSSEY-1 Core", "version": "1.3.0", "status": "nominal"}

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(BASE_DIR, "web", "flight_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>ODYSSEY-1 GCS - Mission Control Center</h1></body></html>"

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        t = 0
        while True:
            t += 1
            mission_api.fsw_state["time"] = t

            # Si la misión está activa, calcular posición en ruta de waypoints
            if mission_path.navigator.is_active:
                lat, lon, alt, seq_status = mission_path.navigator.get_next_position(
                    mission_api.fsw_state["lat"],
                    mission_api.fsw_state["lon"],
                    mission_api.fsw_state["altitude"]
                )
                mission_api.fsw_state["lat"] = lat
                mission_api.fsw_state["lon"] = lon
                mission_api.fsw_state["altitude"] = round(alt, 1)
                mission_api.fsw_state["velocity"] = 12.5  # Velocidad de crucero simulada
                status_text = seq_status
            else:
                status_text = "STANDBY / READY"

            current_alt = mission_api.fsw_state["altitude"]
            current_vel = mission_api.fsw_state["velocity"]
            
            sim_battery = max(15.0, 100.0 - (t * 0.05)) 
            sim_pressure = 15.4 + (0.5 if t % 10 == 0 else 0.0)
            sim_blackout_text = "SOURCE: ACTIVE_MONITORING"

            # --- LÓGICA DE INYECCIÓN DE FALLAS ---
            # Si se activa desde el panel de fallas, modificamos los valores en tiempo real
            if fault_injection.fault_state["low_battery_spike"]:
                sim_battery = 12.5  # Forzar nivel de batería crítico
            
            if fault_injection.fault_state["rf_blackout"]:
                sim_blackout_text = "⚠️ WARNING: RF LINK LOST (BLACKOUT)"

            if fault_injection.fault_state["gps_failure"]:
                status_text = "⚠️ ERROR: 3D GPS FIX LOST"
            # -------------------------------------

            payload_bytes = f"ALT:{current_alt}|VEL:{current_vel}|PC:{sim_pressure}|BAT:{sim_battery}|T:{t}".encode('utf-8')
            crc = hmac.new(b"ODYSSEY_HIL_KEY", payload_bytes, hashlib.sha256).hexdigest()[:4].upper()

            telemetry_packet = {
                "time": t,
                "timestamp": t,
                "altitude": current_alt,
                "velocity": current_vel,
                "speed": current_vel,
                "chamber_pressure": sim_pressure,
                "battery_pct": round(sim_battery, 1),
                "payload": "active",
                "failover": "ready",
                "status": status_text,
                "lat": mission_api.fsw_state["lat"],
                "lon": mission_api.fsw_state["lon"],
                "pitch": 2.5 if mission_path.navigator.is_active else 0.0,
                "yaw": 45.0 if mission_path.navigator.is_active else 0.0,
                "roll": 1.0 if mission_path.navigator.is_active else 0.0,
                "rw_momentum": mission_api.fsw_state["rw_momentum"],
                "crc_valid": True,
                "clock_drift_ms": 0.15,
                "ccsds_frame": f"01AF0008{payload_bytes.hex().upper()[:20]}...{crc}",
                "dsn_station": "Sanarate Ground Station [HIL / RF Link]",
                "blackout_status": sim_blackout_text
            }

            blackbox.log_telemetry_packet(telemetry_packet)
            active_alerts = alerts_engine.check_telemetry_alerts(telemetry_packet)
            telemetry_packet["alerts"] = active_alerts

            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
