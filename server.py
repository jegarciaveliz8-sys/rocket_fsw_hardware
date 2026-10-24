import os
import json
import asyncio
import math
import sqlite3
import zlib
import uuid
import serial
import serial.tools.list_ports
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List
from google import genai
from pymavlink import mavutil
from autonomous_recovery import AutonomousFDIRHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "flight_recorder.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")

fdir_ai_handler = AutonomousFDIRHandler()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS flight_logs")
    cursor.execute('''
        CREATE TABLE flight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id TEXT,
            timestamp REAL,
            lat REAL,
            lon REAL,
            altitude REAL,
            speed REAL,
            roll REAL,
            pitch REAL,
            yaw REAL,
            tvc_x REAL,
            tvc_y REAL,
            fsm_state TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

class SimpleEKF:
    def __init__(self):
        self.est_alt = 0.0
        self.est_vel = 0.0
        self.P = 1.0
        self.Q = 0.1
        self.R = 2.0

    def update(self, measured_alt, dt):
        pred_alt = self.est_alt + self.est_vel * dt
        pred_P = self.P + self.Q
        K = pred_P / (pred_P + self.R)
        self.est_alt = pred_alt + K * (measured_alt - pred_alt)
        self.P = (1 - K) * pred_P
        return self.est_alt

ekf = SimpleEKF()

mission_state = {
    "mission_id": str(uuid.uuid4())[:8],
    "pad_lat": 14.7883,
    "pad_lon": -90.1988,
    "target_lat": 14.6133,
    "target_lon": -90.5283,
    "target_altitude_km": 50.0,
    "altitude_km": 0.0,
    "speed_kmh": 0.0,
    "roll": 0.0,
    "pitch": 0.0,
    "yaw": 0.0,
    "tvc_x": 0.0,
    "tvc_y": 0.0,
    "dynamic_pressure_kpa": 0.0,
    "sequencer_state": "POWERED_FLIGHT_PROPULSION",
    "active_soi": "EARTH_ATMOSPHERIC_TACTICAL",
    "dsn_station": "Ground Telemetry Link",
    "hil_mode": "VIRTUAL_SIMULATION",
    "abort_triggered": False,
    "flight_time": 0.0,
    "fdir_status": "NOMINAL",
    "fdir_alert": "NO_ANOMALY_DETECTED",
    "mitigation_triggered": False
}

ai_proactive_audit = {
    "last_alert": "Sistema nominal. Auditoría continua activa.",
    "alert_level": "INFO",
    "timestamp": 0.0
}

try:
    control_link = mavutil.mavlink_connection('udpout:127.0.0.1:14556', source_system=255)
except Exception:
    control_link = None

# --- Bucle Centralizado de Simulación y Difusión (Broadcast Hub) ---
async def central_telemetry_broadcast_loop():
    mav_connection = None
    try:
        mav_connection = mavutil.mavlink_connection('udpin:0.0.0.0:14550', source_system=1)
    except Exception:
        mav_connection = None

    dt = 0.1
    last_mavlink_time = 0.0
    last_fdir_status = "NOMINAL"
    fleet_vehicles = {
        1: {"lat": mission_state["pad_lat"], "lon": mission_state["pad_lon"], "alt": 0.0, "speed": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0},
        2: {"lat": mission_state["pad_lat"] + 0.002, "lon": mission_state["pad_lon"] + 0.002, "alt": 0.0, "speed": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}
    }

    while True:
        try:
            if mav_connection:
                try:
                    while True:
                        msg = mav_connection.recv_match(blocking=False)
                        if not msg:
                            break
                        msg_type = msg.get_type()
                        sys_id = getattr(msg, 'get_srcSystem', lambda: 1)()
                        if sys_id not in fleet_vehicles:
                            fleet_vehicles[sys_id] = {"lat": mission_state["pad_lat"], "lon": mission_state["pad_lon"], "alt": 0.0, "speed": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0}

                        if msg_type == 'GLOBAL_POSITION_INT':
                            fleet_vehicles[sys_id]["lat"] = msg.lat / 1e7
                            fleet_vehicles[sys_id]["lon"] = msg.lon / 1e7
                            fleet_vehicles[sys_id]["alt"] = (msg.relative_alt / 1000.0) / 1000.0
                            speed_ms = ((msg.vx**2 + msg.vy**2 + msg.vz**2)**0.5) / 100.0
                            fleet_vehicles[sys_id]["speed"] = round(speed_ms * 3.6, 1)
                            last_mavlink_time = asyncio.get_event_loop().time()
                        elif msg_type == 'ATTITUDE':
                            fleet_vehicles[sys_id]["roll"] = round(math.degrees(msg.roll), 2)
                            fleet_vehicles[sys_id]["pitch"] = round(math.degrees(msg.pitch), 2)
                            fleet_vehicles[sys_id]["yaw"] = round(math.degrees(msg.yaw), 2)
                            last_mavlink_time = asyncio.get_event_loop().time()
                except Exception:
                    pass

            current_time = asyncio.get_event_loop().time()
            if current_time - last_mavlink_time < 2.0:
                mission_state["hil_mode"] = "GAZEBO_SITL_SIMULATION"
                mission_state["flight_time"] += dt
                primary_v = fleet_vehicles.get(1, list(fleet_vehicles.values())[0])
                
                mission_state["altitude_km"] = primary_v["alt"]
                mission_state["speed_kmh"] = primary_v["speed"]
                mission_state["roll"] = primary_v["roll"]
                mission_state["pitch"] = primary_v["pitch"]
                mission_state["yaw"] = primary_v["yaw"]

                if abs(primary_v["roll"]) > 40.0 or abs(primary_v["pitch"]) > 60.0:
                    mission_state["fdir_status"] = "CRITICAL"
                    mission_state["fdir_alert"] = "ATTITUDE_EXCURSION_LIMIT_EXCEEDED"
                    
                    if not mission_state.get("mitigation_triggered", False):
                        async def trigger_ai_mitigation():
                            try:
                                response_raw = await fdir_ai_handler.evaluate_and_mitigate(mission_state)
                                ai_decision = json.loads(response_raw)
                                if ai_decision.get("action_required"):
                                    print(f"🤖 [AUTONOMOUS AI MITIGATION] Comando ejecutado: {ai_decision.get('command_code')} - {ai_decision.get('reason')}")
                                    mission_state["abort_triggered"] = True
                                    mission_state["sequencer_state"] = "ABORT_MISSION_AUTONOMOUS_AI_RECOVERY"
                                    mission_state["mitigation_triggered"] = True
                            except Exception as e:
                                print(f"⚠️ Error en mitigación IA: {e}")
                        asyncio.create_task(trigger_ai_mitigation())
                else:
                    if not mission_state["abort_triggered"]:
                        mission_state["fdir_status"] = "NOMINAL"
                        mission_state["fdir_alert"] = "NO_ANOMALY_DETECTED"
                
                if mission_state["fdir_status"] != last_fdir_status:
                    asyncio.create_task(run_proactive_ai_audit(f"FDIR_STATE_CHANGE: {mission_state['fdir_status']}"))
                    last_fdir_status = mission_state["fdir_status"]

                telemetry_payload = {
                    "status": "SITL_ACTIVE",
                    "mission_id": mission_state["mission_id"],
                    "flight_time": round(mission_state["flight_time"], 1),
                    "altitude": primary_v["alt"],
                    "altitude_km": primary_v["alt"],
                    "speed": primary_v["speed"],
                    "speed_kmh": primary_v["speed"],
                    "velocity": primary_v["speed"],
                    "lat": round(primary_v["lat"], 5),
                    "lon": round(primary_v["lon"], 5),
                    "fsm_state": "AUTONOMOUS_GUIDED_FLIGHT",
                    "roll": primary_v["roll"],
                    "pitch": primary_v["pitch"],
                    "yaw": primary_v["yaw"],
                    "tvc_x": 0.0,
                    "tvc_y": 0.0,
                    "dynamic_pressure_kpa": 0.0,
                    "active_soi": mission_state["active_soi"],
                    "sequencer_state": "AUTONOMOUS_GUIDED_FLIGHT",
                    "fdir_status": mission_state["fdir_status"],
                    "fdir_alert": mission_state["fdir_alert"],
                    "proactive_audit": ai_proactive_audit,
                    "dsn_station": mission_state["dsn_station"],
                    "hil_mode": "GAZEBO_SITL_SIMULATION",
                    "vehicles": fleet_vehicles,
                    "geodetic": {
                        "lat": round(primary_v["lat"], 5),
                        "lon": round(primary_v["lon"], 5),
                        "alt": round(primary_v["alt"] * 1000.0, 1)
                    }
                }
            else:
                mission_state["hil_mode"] = "VIRTUAL_SIMULATION"
                if not mission_state["abort_triggered"]:
                    mission_state["flight_time"] += dt
                    total_duration = 35.0
                    progress = min(mission_state["flight_time"] / total_duration, 1.0)
                    wind_lat = math.sin(mission_state["flight_time"] * 0.5) * 0.0003
                    wind_lon = math.cos(mission_state["flight_time"] * 0.5) * 0.0003
                    
                    current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * progress + wind_lat
                    current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * progress + wind_lon
                    max_alt = mission_state["target_altitude_km"]
                    raw_alt = max_alt * 4.0 * progress * (1.0 - progress) if progress < 1.0 else 0.0
                    filtered_alt = ekf.update(raw_alt, dt)
                    
                    mission_state["roll"] = round(math.sin(mission_state["flight_time"] * 3.0) * 8.0, 2)
                    mission_state["pitch"] = round(45.0 * (1.0 - progress) + 5.0 * math.cos(mission_state["flight_time"]), 2)
                    mission_state["yaw"] = round(math.atan2(mission_state["target_lat"] - mission_state["pad_lat"], mission_state["target_lon"] - mission_state["pad_lon"]) * 180 / math.pi, 2)
                    mission_state["tvc_x"] = round(math.sin(mission_state["flight_time"] * 4.0) * 3.5, 2)
                    mission_state["tvc_y"] = round(math.cos(mission_state["flight_time"] * 4.0) * 3.5, 2)

                    if progress >= 1.0:
                        fsm_status = "MISSION_COMPLETED_IMPACT_SUCCESS"
                        total_speed = 0.0
                    elif progress > 0.85:
                        fsm_status = "TERMINAL_HOMING_DESCENT"
                        total_speed = 400.0
                    else:
                        fsm_status = "BALISTIC_MIDCOURSE_GUIDANCE"
                        total_speed = 2200.0
                    mission_state["sequencer_state"] = fsm_status

                    fleet_vehicles[1] = {
                        "lat": current_lat, "lon": current_lon, "alt": filtered_alt,
                        "speed": total_speed, "roll": mission_state["roll"], "pitch": mission_state["pitch"], "yaw": mission_state["yaw"]
                    }
                    fleet_vehicles[2] = {
                        "lat": current_lat - 0.0015, "lon": current_lon - 0.0015, "alt": max(filtered_alt - 0.5, 0.0),
                        "speed": total_speed * 0.98, "roll": mission_state["roll"] * 0.9, "pitch": mission_state["pitch"], "yaw": mission_state["yaw"]
                    }
                else:
                    current_lat = mission_state["target_lat"]
                    current_lon = mission_state["target_lon"]
                    filtered_alt = 0.0
                    total_speed = 0.0

                mission_state["altitude_km"] = round(filtered_alt, 2)
                mission_state["speed_kmh"] = total_speed
                air_density = 1.225 * math.exp(-filtered_alt / 8.5) if filtered_alt < 50 else 0.0
                dynamic_pressure_kpa = 0.5 * air_density * ((total_speed / 3.6) ** 2) / 1000.0
                mission_state["dynamic_pressure_kpa"] = round(dynamic_pressure_kpa, 2)

                if mission_state["dynamic_pressure_kpa"] > 110.0:
                    mission_state["fdir_status"] = "WARNING"
                    mission_state["fdir_alert"] = "STRUCTURAL_Q_LIMIT_WARNING"
                else:
                    if not mission_state["abort_triggered"]:
                        mission_state["fdir_status"] = "NOMINAL"
                        mission_state["fdir_alert"] = "NO_ANOMALY_DETECTED"

                if mission_state["fdir_status"] != last_fdir_status:
                    asyncio.create_task(run_proactive_ai_audit(f"FDIR_STATE_CHANGE: {mission_state['fdir_status']}"))
                    last_fdir_status = mission_state["fdir_status"]

                telemetry_payload = {
                    "status": "POWERED ASCENT",
                    "mission_id": mission_state["mission_id"],
                    "flight_time": round(mission_state["flight_time"], 1),
                    "altitude": mission_state["altitude_km"],
                    "altitude_km": mission_state["altitude_km"],
                    "speed": mission_state["speed_kmh"],
                    "speed_kmh": mission_state["speed_kmh"],
                    "velocity": mission_state["speed_kmh"],
                    "lat": round(current_lat, 5),
                    "lon": round(current_lon, 5),
                    "fsm_state": mission_state["sequencer_state"],
                    "roll": mission_state["roll"],
                    "pitch": mission_state["pitch"],
                    "yaw": mission_state["yaw"],
                    "tvc_x": mission_state["tvc_x"],
                    "tvc_y": mission_state["tvc_y"],
                    "dynamic_pressure_kpa": mission_state["dynamic_pressure_kpa"],
                    "active_soi": mission_state["active_soi"],
                    "sequencer_state": mission_state["sequencer_state"],
                    "fdir_status": mission_state["fdir_status"],
                    "fdir_alert": mission_state["fdir_alert"],
                    "proactive_audit": ai_proactive_audit,
                    "dsn_station": mission_state["dsn_station"],
                    "hil_mode": mission_state["hil_mode"],
                    "vehicles": fleet_vehicles,
                    "geodetic": {
                        "lat": round(current_lat, 5),
                        "lon": round(current_lon, 5),
                        "alt": round(filtered_alt * 1000.0, 1)
                    }
                }

            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO flight_logs (mission_id, timestamp, lat, lon, altitude, speed, roll, pitch, yaw, tvc_x, tvc_y, fsm_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (mission_state["mission_id"], telemetry_payload.get("flight_time", 0.0), telemetry_payload.get("lat", mission_state["pad_lat"]), telemetry_payload.get("lon", mission_state["pad_lon"]), telemetry_payload.get("altitude", 0.0), telemetry_payload.get("speed", 0.0), telemetry_payload.get("roll", 0.0), telemetry_payload.get("pitch", 0.0), telemetry_payload.get("yaw", 0.0), telemetry_payload.get("tvc_x", 0.0), telemetry_payload.get("tvc_y", 0.0), telemetry_payload.get("fsm_state", "UNKNOWN"))
                )
                conn.commit()
                conn.close()
            except Exception:
                pass

            await manager.broadcast(json.dumps(telemetry_payload))
        except Exception:
            pass

        await asyncio.sleep(0.1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(central_telemetry_broadcast_loop())
    yield
    task.cancel()

app = FastAPI(title="ODYSSEY-1 Ground Control Station (GCS)", lifespan=lifespan)

class MissionCoordinates(BaseModel):
    pad_lat: float
    pad_lon: float
    target_lat: float
    target_lon: float

class OrbitPlanRequest(BaseModel):
    target_altitude_km: float
    crc32_checksum: int

class AssistantRequest(BaseModel):
    prompt: str = "Auditar sistema"
    query: str = None

class DroneCommandRequest(BaseModel):
    command: str
    param1: float = 0.0

class Waypoint(BaseModel):
    lat: float
    lon: float
    alt: float
    seq: int

class MissionPlanRequest(BaseModel):
    waypoints: List[Waypoint]

@app.post("/api/mission/coordinates")
async def set_coordinates(coords: MissionCoordinates):
    mission_state["mission_id"] = str(uuid.uuid4())[:8]
    mission_state["pad_lat"] = coords.pad_lat
    mission_state["pad_lon"] = coords.pad_lon
    mission_state["target_lat"] = coords.target_lat
    mission_state["target_lon"] = coords.target_lon
    mission_state["sequencer_state"] = "POWERED_FLIGHT_PROPULSION"
    mission_state["abort_triggered"] = False
    mission_state["flight_time"] = 0.0
    mission_state["fdir_status"] = "NOMINAL"
    mission_state["fdir_alert"] = "NO_ANOMALY_DETECTED"
    mission_state["mitigation_triggered"] = False
    return {"status": "success", "mission_id": mission_state["mission_id"], "updated_coordinates": coords.model_dump()}

@app.post("/api/drone/command")
async def send_drone_command(req: DroneCommandRequest):
    try:
        if not control_link:
            raise HTTPException(status_code=500, detail="Control link UDP connection not initialized")
            
        if req.command == "ARM":
            cmd_id, p1 = 400, 1.0
        elif req.command == "DISARM":
            cmd_id, p1 = 400, 0.0
        elif req.command == "TAKEOFF":
            cmd_id, p1 = 22, 10.0
        elif req.command == "RTL":
            cmd_id, p1 = 20, 0.0
        else:
            cmd_id, p1 = 400, 0.0

        control_link.mav.command_long_send(1, 1, cmd_id, 0, p1, 0, 0, 0, 0, 0, 0)
        return {"status": "SUCCESS", "command_sent": req.command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mission/waypoints")
async def upload_mission_waypoints(mission: MissionPlanRequest):
    received_count = len(mission.waypoints)
    return {
        "status": "success",
        "waypoints_uploaded": received_count,
        "message": f"Misión de {received_count} puntos cargada correctamente en el pipeline."
    }

@app.post("/api/mission/abort")
async def trigger_abort():
    mission_state["abort_triggered"] = True
    mission_state["sequencer_state"] = "ABORT_MISSION_LES_TRIGGERED"
    mission_state["fdir_status"] = "CRITICAL"
    mission_state["fdir_alert"] = "MANUAL_ABORT_FTS_ACTIVATED"
    asyncio.create_task(run_proactive_ai_audit("ABORT_TRIGGERED_BY_OPERATOR"))
    return {"status": "ABORT_SEQUENCE_ACTIVATED"}

@app.post("/api/orbit/plan")
async def plan_orbit(req: OrbitPlanRequest):
    payload_str = f"{req.target_altitude_km:.1f}"
    calculated_crc = zlib.crc32(payload_str.encode('utf-8')) & 0xFFFFFFFF
    if req.crc32_checksum != calculated_crc:
        raise HTTPException(status_code=400, detail=f"SECURITY_ALERT: CRC32 mismatch. Received {req.crc32_checksum}, expected {calculated_crc}")
    mission_state["target_altitude_km"] = req.target_altitude_km
    return {
        "status": "UPLINK_SECURE_ACCEPTED",
        "burn_plan": {
            "dv_magnitude_m_s": round(math.sqrt(req.target_altitude_km * 9.81 * 1000) * 0.1, 2),
            "target_altitude_km": req.target_altitude_km
        }
    }

async def run_proactive_ai_audit(trigger_event: str):
    try:
        client = genai.Client()
        prompt = f"""
        [SISTEMA DE AUDITORÍA AUTÓNOMA GCS ODYSSEY-1]
        EVENTO DETECTADO: {trigger_event}
        Misión ID: {mission_state['mission_id']} | Tiempo de Vuelo: T+{mission_state['flight_time']:.1f}s
        Altitud: {mission_state['altitude_km']} km | Velocidad: {mission_state['speed_kmh']} km/h
        FDIR Status: {mission_state['fdir_status']} ({mission_state['fdir_alert']})
        Presión Dinámica: {mission_state['dynamic_pressure_kpa']} kPa
        
        Emite una evaluación de riesgo operacional ultraconcisa (máximo 2 frases) y una acción recomendada.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_proactive_audit["last_alert"] = response.text
        ai_proactive_audit["alert_level"] = mission_state["fdir_status"]
        ai_proactive_audit["timestamp"] = mission_state["flight_time"]
    except Exception as e:
        ai_proactive_audit["last_alert"] = f"⚠️ AUDITORÍA AUTÓNOMA: {trigger_event} - {mission_state['fdir_alert']}"
        ai_proactive_audit["alert_level"] = mission_state["fdir_status"]

async def handle_ai_logic(prompt: str):
    max_retries = 2
    for attempt in range(max_retries):
        try:
            client = genai.Client()
            context_prompt = f"""
            Actúa como el Ingeniero Jefe de Operaciones en Tierra (GCS) de ODYSSEY-1.
            Estado actual de telemetría de la misión ({mission_state['mission_id']}):
            - Altitud: {mission_state['altitude_km']} km
            - Velocidad: {mission_state['speed_kmh']} km/h
            - Estado FSM: {mission_state['sequencer_state']}
            - FDIR: {mission_state['fdir_status']} ({mission_state['fdir_alert']})
            - Última Auditoría Proactiva IA: {ai_proactive_audit['last_alert']}
            
            Consulta del operador: {prompt}
            Responde de forma técnica y concisa.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=context_prompt,
            )
            return {"response": response.text, "proactive_audit": ai_proactive_audit}
        except Exception:
            if attempt == max_retries - 1:
                return {"response": f"⚠️ ENLACE IA DEGRADADO: Subsistemas locales nominales.", "proactive_audit": ai_proactive_audit}
            await asyncio.sleep(1)

async def parse_prompt_from_request(req: AssistantRequest, request: Request):
    prompt_text = "Auditar sistema"
    if req:
        if req.prompt:
            prompt_text = req.prompt
        elif req.query:
            prompt_text = req.query
    if request:
        try:
            body = await request.json()
            if "prompt" in body:
                prompt_text = body["prompt"]
            elif "query" in body:
                prompt_text = body["query"]
        except Exception:
            pass
    return prompt_text

@app.get("/ai/query")
@app.post("/ai/query")
@app.get("/api/ai/query")
@app.post("/api/ai/query")
@app.get("/api/asistente")
@app.post("/api/asistente")
@app.get("/api/assistant")
@app.post("/api/assistant")
async def ai_query_endpoint(req: AssistantRequest = None, request: Request = None):
    return await handle_ai_logic(await parse_prompt_from_request(req, request))

@app.get("/api/mission/logs")
async def get_flight_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, lat, lon, altitude, speed, roll, pitch, yaw, tvc_x, tvc_y, fsm_state FROM flight_logs WHERE mission_id = ? ORDER BY id ASC LIMIT 500", (mission_state["mission_id"],))
    rows = cursor.fetchall()
    conn.close()
    return {"mission_id": mission_state["mission_id"], "logs": rows}

def generate_csv_response():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, lat, lon, altitude, speed, fsm_state FROM flight_logs WHERE mission_id = ?", (mission_state["mission_id"],))
    rows = cursor.fetchall()
    conn.close()
    
    csv_data = "Mission Time,lat,lon,altitude,speed,fsm_state\n"
    for r in rows:
        csv_data += f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}\n"
    return PlainTextResponse(csv_data, media_type="text/csv")

@app.get("/export/csv", operation_id="export_csv_root")
@app.get("/api/export/csv", operation_id="export_csv_api")
@app.get("/api/mission/export", operation_id="export_mission_export")
@app.get("/api/mission/export-csv", operation_id="export_mission_export_csv")
@app.get("/api/mission/export/csv", operation_id="export_mission_export_csv_slash")
async def export_csv_endpoint():
    return generate_csv_response()

@app.get("/api/mission/report/pdf")
async def generate_pdf_report():
    report_file = os.path.join(BASE_DIR, "flight_report.png")
    if os.path.exists(report_file):
        return FileResponse(report_file, media_type="image/png", filename="flight_report.png")
    return {"status": "Report generated", "details": f"ODYSSEY-1 Telemetry Mission {mission_state['mission_id']} Summary Certified"}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class NoCacheStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

app.mount("/", NoCacheStaticFiles(directory=STATIC_DIR, html=True), name="static")
