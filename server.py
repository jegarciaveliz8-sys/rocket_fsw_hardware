from fastapi import Response
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import hashlib
import hmac
import math
import uvicorn
from dotenv import load_dotenv

# Carga obligatoria del archivo .env al arrancar el servidor
load_dotenv()

from database import init_db, log_telemetry

app = FastAPI(
    title="ODYSSEY-1 Modular Mission Control Center",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Base de datos de telemetría (odyssey_telemetry.db) inicializada.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(BASE_DIR, "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

# Importación de todos los routers modulares
from routers import (
    mission_api, subsystems_api, ai_copilot, dji_bridge, alerts_engine, 
    blackbox, commands_api, mission_path, fault_injection, mission_planner, 
    stations_api, mission_uplink, auth_manager, dsn_network,
    mission, orbit_math, telemetry_export, timeline, video_feed,
    network_sim, security, timeseries, swarm, tactical, hil, auth,
    dvr, reports, field_assistant, payload_science, weather, fdir,
    audit, blackbox_replay, monte_carlo, replay_engine, pdf_reports, telemetry_mqtt
)
from routers.stations_api import get_active_station_telemetry, get_dynamic_dsn_station

# Registro de routers
app.include_router(mission_api.router)
app.include_router(subsystems_api.router)
app.include_router(ai_copilot.router)
app.include_router(dji_bridge.router)
app.include_router(commands_api.router)
app.include_router(fault_injection.router)
app.include_router(mission_planner.router)
app.include_router(stations_api.router)
app.include_router(mission_uplink.router)
app.include_router(auth_manager.router)
app.include_router(dsn_network.router)
app.include_router(mission.router)
app.include_router(orbit_math.router)
app.include_router(telemetry_export.router)
app.include_router(timeline.router)
app.include_router(video_feed.router)
app.include_router(network_sim.router)
app.include_router(security.router)
app.include_router(timeseries.router)
app.include_router(swarm.router)
app.include_router(tactical.router)
app.include_router(hil.router)
app.include_router(auth.router)
app.include_router(dvr.router)
app.include_router(reports.router)
app.include_router(field_assistant.router)
app.include_router(payload_science.router)
app.include_router(weather.router)
app.include_router(fdir.router)
app.include_router(audit.router)
app.include_router(blackbox_replay.router)
app.include_router(monte_carlo.router)
app.include_router(replay_engine.router)
app.include_router(pdf_reports.router)
app.include_router(telemetry_mqtt.router)

BASE_LAT, BASE_LON = 14.7883, -90.1988

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# WebSocket de Telemetría en Vivo
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        t = 0
        while True:
            t += 1
            mission_api.fsw_state["time"] = t

            status_text = "POWERED ASCENT" if mission_path.navigator.is_active else "STANDBY / NOMINAL"
            
            # Forzar siempre valores orbitales nominales base para garantizar datos en vivo
            current_alt = 401500.0  # ~401 km
            current_vel = 7668.5    # m/s

            if mission_path.navigator.is_active:
                current_state = mission_api.fsw_state.copy()
                updated_state = mission_path.navigator.update_position(current_state)
                mission_api.fsw_state["lat"] = updated_state["lat"]
                mission_api.fsw_state["lon"] = updated_state["lon"]
                current_alt = round(updated_state.get("altitude", current_alt), 1)
                current_vel = updated_state.get("velocity", current_vel)
            
            current_lat = mission_api.fsw_state.get("lat", BASE_LAT)
            current_lon = mission_api.fsw_state.get("lon", BASE_LON)
            
            sim_battery = max(15.0, 100.0 - (t * 0.05))  
            sim_pressure = 15.4 + (0.5 if t % 10 == 0 else 0.0)
            sim_blackout_text = "SOURCE: ACTIVE_MONITORING"

            distance_from_base = calculate_distance(BASE_LAT, BASE_LON, current_lat, current_lon)
            if distance_from_base > 5000000.0:
                status_text = "🚨 GEOFENCE BREACHED: RTL ACTIVADO"

            if fault_injection.fault_state["low_battery_spike"]:
                sim_battery = 12.5  
            
            if fault_injection.fault_state["rf_blackout"]:
                sim_blackout_text = "⚠️ WARNING: RF LINK LOST (BLACKOUT)"

            if fault_injection.fault_state["gps_failure"]:
                status_text = "⚠️ ERROR: 3D GPS FIX LOST"

            dsn_info = get_dynamic_dsn_station(distance_from_base)
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
                "lat": current_lat,
                "lon": current_lon,
                "pitch": 2.5 if mission_path.navigator.is_active else 0.0,
                "yaw": 45.0 if mission_path.navigator.is_active else 0.0,
                "roll": 1.0 if mission_path.navigator.is_active else 0.0,
                "rw_momentum": mission_api.fsw_state.get("rw_momentum", 0.0),
                "crc_valid": True,
                "clock_drift_ms": 0.15,
                "ccsds_frame": f"01AF0008{payload_bytes.hex().upper()[:20]}...{crc}",
                "dsn_station": get_active_station_telemetry()["dsn_station"],
                "snr": dsn_info["snr"],
                "stations_status": dsn_info["stations_status"],
                "blackout_status": sim_blackout_text,
                "distance_from_base_m": round(distance_from_base, 1)
            }

            blackbox.log_telemetry_packet(telemetry_packet)
            active_alerts = alerts_engine.check_telemetry_alerts(telemetry_packet)
            telemetry_packet["alerts"] = active_alerts

            log_telemetry(telemetry_packet)
            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

# Rutas de Vistas HTML Modulares
@app.get("/", response_class=HTMLResponse)
def get_root_flight_deck():
    path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Index HTML no encontrado</h1>"

@app.get("/command", response_class=HTMLResponse)
def get_command_panel():
    path = os.path.join(BASE_DIR, "web", "command_panel.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Command Panel no encontrado</h1>"

@app.get("/engineering", response_class=HTMLResponse)
def get_engineering_console():
    path = os.path.join(BASE_DIR, "web", "engineering.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Engineering Console no encontrado</h1>"

@app.get("/orbit", response_class=HTMLResponse)
def get_orbit_panel():
    path = os.path.join(BASE_DIR, "web", "orbit.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Orbit Panel no encontrado</h1>"

@app.get("/payload", response_class=HTMLResponse)
def get_payload_panel():
    path = os.path.join(BASE_DIR, "web", "payload.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Payload Panel no encontrado</h1>"

@app.get("/montecarlo", response_class=HTMLResponse)
def get_montecarlo_panel():
    path = os.path.join(BASE_DIR, "web", "montecarlo.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Monte Carlo Panel no encontrado</h1>"

@app.get("/replay", response_class=HTMLResponse)
def get_replay_panel():
    path = os.path.join(BASE_DIR, "web", "replay.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Replay Panel no encontrado</h1>"

@app.get("/ui")
def get_ui_info():
    return {"version": "1.3.0", "system": "ODYSSEY-1 GCS"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

from pydantic import BaseModel

class LaunchPadConfig(BaseModel):
    lat: float
    lon: float

@app.post("/api/mission/set-launch-pad")
def set_launch_pad(config: LaunchPadConfig):
    global BASE_LAT, BASE_LON
    BASE_LAT = config.lat
    BASE_LON = config.lon
    print(f"🌍 Base de salida global actualizada a: [{BASE_LAT}, {BASE_LON}]")
    return {
        "status": "SUCCESS", 
        "message": f"Base redefinida a [{BASE_LAT}, {BASE_LON}]"
    }

import requests

class NamedMissionRequest(BaseModel):
    base_name: str
    target_name: str

def geocode_place(place_name: str):
    url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(place_name)}&format=json&limit=1"
    headers = {'User-Agent': 'Odyssey1-GCS/1.3'}
    res = requests.get(url, headers=headers)
    data = res.json()
    if data and len(data) > 0:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon, data[0].get('display_name', place_name)
    raise ValueError(f"No se pudieron encontrar coordenadas para: {place_name}")

@app.post("/api/mission/named-flight")
def start_named_mission(config: NamedMissionRequest):
    global BASE_LAT, BASE_LON
    try:
        b_lat, b_lon, b_formatted = geocode_place(config.base_name)
        t_lat, t_lon, t_formatted = geocode_place(config.target_name)

        BASE_LAT, BASE_LON = b_lat, b_lon

        dist_meters = calculate_distance(b_lat, b_lon, t_lat, t_lon)
        dist_km = round(dist_meters / 1000.0, 2)
        cruise_altitude = max(3000.0, min(dist_meters * 0.05, 40000.0))

        waypoints = [
            {"lat": b_lat, "lon": b_lon, "alt": 100.0, "loiter": 2, "name": f"Base: {b_formatted}"},
            {"lat": t_lat, "lon": t_lon, "alt": cruise_altitude, "loiter": 15, "name": f"Objetivo: {t_formatted}", "action": "AUTO_PAYLOAD_CAPTURE"},
            {"lat": b_lat, "lon": b_lon, "alt": 0.0, "loiter": 0, "name": "RTL (Return to Launch Base)"}
        ]
        
        mission_path.navigator.set_waypoints(waypoints)
        mission_path.navigator.is_active = True

        return {
            "status": "SUCCESS",
            "message": f"Misión programada hacia '{t_formatted}' ({dist_km} km). Captura de payload y RTL activos.",
            "distance_km": dist_km,
            "base": {"lat": b_lat, "lon": b_lon, "name": b_formatted},
            "target": {"lat": t_lat, "lon": t_lon, "name": t_formatted}
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
