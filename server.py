import os
import json
import asyncio
import math
import sqlite3
import zlib
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="ODYSSEY-1 Aerospace FSW & Mission Control")

DB_FILE = "flight_recorder.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_logs (
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
    "pitch": 45.0,
    "yaw": 0.0,
    "tvc_x": 0.0,
    "tvc_y": 0.0,
    "dynamic_pressure_kpa": 0.0,
    "sequencer_state": "POWERED_FLIGHT_PROPULSION",
    "active_soi": "EARTH_ATMOSPHERIC_TACTICAL",
    "dsn_station": "Guatemala Tactical Link",
    "hil_mode": "VIRTUAL_SIMULATION",
    "abort_triggered": False,
    "flight_time": 0.0,
    "fdir_status": "NOMINAL",
    "fdir_alert": "NO_ANOMALY_DETECTED"
}

class MissionCoordinates(BaseModel):
    pad_lat: float
    pad_lon: float
    target_lat: float
    target_lon: float

class OrbitPlanRequest(BaseModel):
    target_altitude_km: float
    crc32_checksum: int

class AssistantRequest(BaseModel):
    prompt: str

def evaluate_fdir():
    if abs(mission_state["tvc_x"]) > 4.5 or abs(mission_state["tvc_y"]) > 4.5:
        mission_state["fdir_status"] = "WARNING"
        mission_state["fdir_alert"] = "TVC_MAX_GIMBAL_EXCURSION"
    elif mission_state["speed_kmh"] > 2500 or mission_state.get("dynamic_pressure_kpa", 0) > 50:
        mission_state["fdir_status"] = "ALERT"
        mission_state["fdir_alert"] = "AERODYNAMIC_OVERPOWER_MAX_Q"
    else:
        mission_state["fdir_status"] = "NOMINAL"
        mission_state["fdir_alert"] = "SYSTEMS_OPTIMAL"

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
    return {"status": "success", "mission_id": mission_state["mission_id"], "updated_coordinates": coords.dict()}

@app.post("/api/mission/abort")
async def trigger_abort():
    mission_state["abort_triggered"] = True
    mission_state["sequencer_state"] = "ABORT_MISSION_LES_TRIGGERED"
    mission_state["fdir_status"] = "CRITICAL"
    mission_state["fdir_alert"] = "MANUAL_ABORT_FTS_ACTIVATED"
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

@app.post("/api/asistente")
async def field_assistant(req: AssistantRequest):
    try:
        client = genai.Client()
        context_prompt = f"""
        Actúa como el Ingeniero Jefe de Software de Vuelo en el Centro de Control ODYSSEY-1.
        Estado actual de la telemetría de la nave (Misión ID: {mission_state['mission_id']}):
        - Altitud EKF: {mission_state['altitude_km']} km
        - Velocidad: {mission_state['speed_kmh']} km/h
        - Presión Dinámica (Max Q): {mission_state.get('dynamic_pressure_kpa', 0)} kPa
        - Secuenciador FSM: {mission_state['sequencer_state']}
        - Estado FDIR: {mission_state['fdir_status']} ({mission_state['fdir_alert']})
        - Actitud (Roll, Pitch, Yaw): {mission_state['roll']}°, {mission_state['pitch']}°, {mission_state['yaw']}°
        
        Pregunta del operador de campo: {req.prompt}
        Responde de manera técnica, profesional y concisa utilizando terminología aeroespacial.
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=context_prompt,
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": f"❌ Error conectando con Gemini API: {str(e)}"}

@app.get("/api/mission/logs")
async def get_flight_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, lat, lon, altitude, speed, roll, pitch, yaw, tvc_x, tvc_y, fsm_state FROM flight_logs WHERE mission_id = ? ORDER BY id ASC LIMIT 500", (mission_state["mission_id"],))
    rows = cursor.fetchall()
    conn.close()
    return {"mission_id": mission_state["mission_id"], "logs": rows}

@app.get("/api/mission/report/pdf")
async def generate_pdf_report():
    report_file = "flight_report.png"
    if os.path.exists(report_file):
        return FileResponse(report_file, media_type="image/png", filename="flight_report.png")
    return {"status": "Report generated", "details": f"ODYSSEY-1 Telemetry Mission {mission_state['mission_id']} Summary Certified"}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    dt = 0.1
    try:
        while True:
            if not mission_state["abort_triggered"]:
                mission_state["flight_time"] += dt
                total_duration = 35.0
                progress = min(mission_state["flight_time"] / total_duration, 1.0)
                
                wind_drift_lat = math.sin(mission_state["flight_time"] * 0.5) * 0.0003
                wind_drift_lon = math.cos(mission_state["flight_time"] * 0.5) * 0.0003
                
                current_lat = mission_state["pad_lat"] + (mission_state["target_lat"] - mission_state["pad_lat"]) * progress + wind_drift_lat
                current_lon = mission_state["pad_lon"] + (mission_state["target_lon"] - mission_state["pad_lon"]) * progress + wind_drift_lon
                
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

            evaluate_fdir()

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO flight_logs (mission_id, timestamp, lat, lon, altitude, speed, roll, pitch, yaw, tvc_x, tvc_y, fsm_state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (mission_state["mission_id"], mission_state["flight_time"], current_lat, current_lon, mission_state["altitude_km"], mission_state["speed_kmh"], mission_state["roll"], mission_state["pitch"], mission_state["yaw"], mission_state["tvc_x"], mission_state["tvc_y"], mission_state["sequencer_state"])
            )
            conn.commit()
            conn.close()

            telemetry_payload = {
                "mission_id": mission_state["mission_id"],
                "flight_time": round(mission_state["flight_time"], 1),
                "altitude_km": mission_state["altitude_km"],
                "speed_kmh": mission_state["speed_kmh"],
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
                "dsn_station": mission_state["dsn_station"],
                "hil_mode": mission_state["hil_mode"],
                "geodetic": {
                    "lat": round(current_lat, 5),
                    "lon": round(current_lon, 5),
                    "alt": round(filtered_alt * 1000.0, 1)
                }
            }
            await websocket.send_text(json.dumps(telemetry_payload))
            await asyncio.sleep(0.3)
    except WebSocketDisconnect:
        pass

app.mount("/", StaticFiles(directory="static", html=True), name="static")
