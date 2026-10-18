import asyncio
import math
import json
import os
import logging
import csv
import io
import struct
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import databases
import sqlalchemy
import serial
from ekf_filter import RocketEKF

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from crccheck.crc import Crc16CcittFalse

logging.basicConfig(filename="mission_audit.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./mission_telemetry.db")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

telemetry_table = sqlalchemy.Table(
    "telemetry_logs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("mission_id", sqlalchemy.Integer, default=1),
    sqlalchemy.Column("mission_time", sqlalchemy.Integer),
    sqlalchemy.Column("altitude", sqlalchemy.Float),
    sqlalchemy.Column("velocity", sqlalchemy.Float),
    sqlalchemy.Column("status", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await database.connect()
    except Exception:
        pass
    yield
    try:
        await database.disconnect()
    except Exception:
        pass

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ai_client = None
if os.environ.get("GEMINI_API_KEY"):
    ai_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

latest_telemetry = {"time": 0, "altitude": 0.0, "velocity": 0.0, "status": "STANDBY"}

GROUND_STATIONS = {
    "Cape Canaveral": {"lat": 28.5721, "lon": -80.6480},
    "Madrid DSN": {"lat": 40.4262, "lon": -4.2497},
    "Goldstone DSN": {"lat": 35.4266, "lon": -116.8900},
    "Canberra DSN": {"lat": -35.4014, "lon": 148.9817}
}

def build_ccsds_packet(apid: int, seq_count: int, payload_bytes: bytes) -> bytes:
    packet_version_type_flag = 0x0800 | (apid & 0x07FF)
    sequence_control = 0xC000 | (seq_count & 0x3FFF)
    packet_length = len(payload_bytes) + 2 - 1
    header = struct.pack(">HHH", packet_version_type_flag, sequence_control, packet_length)
    packet_without_crc = header + payload_bytes
    crc = Crc16CcittFalse.calc(packet_without_crc)
    return packet_without_crc + struct.pack(">H", crc)

def calculate_active_ground_station(rocket_lat, rocket_lon):
    best_station = "Cape Canaveral"
    min_dist = 999999.0
    for name, coords in GROUND_STATIONS.items():
        d = math.sqrt((rocket_lat - coords["lat"])**2 + (rocket_lon - coords["lon"])**2)
        if d < min_dist:
            min_dist = d
            best_station = name
    return best_station

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    if os.path.exists("web/flight_dashboard.html"):
        with open("web/flight_dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>web/flight_dashboard.html no encontrado</h1>"

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    global latest_telemetry
    await websocket.accept()
    kalman = RocketEKF()
    mission_time = 0
    raw_altitude = 0.0
    raw_velocity = 0.0
    lat, lon = 28.5721, -80.6480
    mission_state = "STANDBY"
    current_mission_id = 1
    stage = "STAGE_1_BOOST"
    parachute_deployed = False
    seq_counter = 0

    # Intento de enlace con puerto serie HIL
    serial_port = None
    if os.path.exists("/tmp/ttyV0"):
        try:
            serial_port = serial.Serial('/tmp/ttyV0', 115200, timeout=0.05)
        except Exception:
            pass

    if database.is_connected:
        try:
            query = sqlalchemy.select(sqlalchemy.func.max(telemetry_table.c.mission_id))
            res = await database.fetch_val(query)
            current_mission_id = (res or 0) + 1
        except Exception:
            pass

    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.05)
                packet = json.loads(msg)
                cmd = packet.get("command")
                if cmd == "LAUNCH":
                    mission_state = "POWERED ASCENT"
                    stage = "STAGE_1_BOOST"
                    parachute_deployed = False
                elif cmd == "ABORT":
                    mission_state = "CATASTROPHIC FAILURE"
                elif cmd == "RESET":
                    mission_state = "STANDBY"
                    mission_time = 0
                    raw_altitude, raw_velocity = 0.0, 0.0
                    stage = "STAGE_1_BOOST"
                    parachute_deployed = False
                    kalman = RocketEKF()
                    current_mission_id += 1
            except asyncio.TimeoutError:
                pass

            # HIL Check
            if serial_port and serial_port.in_waiting > 0:
                try:
                    line = serial_port.readline().decode('utf-8').strip()
                    hw_data = json.loads(line)
                    raw_altitude = hw_data.get("altitude", raw_altitude)
                    raw_velocity = hw_data.get("velocity", raw_velocity)
                    mission_time = hw_data.get("time", mission_time)
                except Exception:
                    pass
            else:
                # Simulación física del Gemelo Digital (Etapas y Paracaídas)
                if mission_state == "POWERED ASCENT":
                    mission_time += 1
                    if mission_time <= 40:
                        stage = "STAGE_1_BOOST"
                        raw_altitude += 0.25 + (mission_time * 0.003)
                        raw_velocity += 65.0 + (mission_time * 1.1)
                        pitch = max(30.0, 90.0 - (mission_time * 1.2))
                    elif 40 < mission_time <= 45:
                        stage = "STAGE_SEPARATION"
                        raw_altitude += 0.10
                        pitch = 20.0
                    elif 45 < mission_time <= 90:
                        stage = "STAGE_2_IGNITION"
                        raw_altitude += 0.55 + (mission_time * 0.008)
                        raw_velocity += 120.0 + (mission_time * 1.5)
                        pitch = 5.0
                    elif mission_time > 90 and raw_altitude > 100.0:
                        mission_state = "ORBITAL INJECTION (LEO)"
                        stage = "ORBIT_LEO"
                        pitch = 0.0

                elif mission_state == "CATASTROPHIC FAILURE" or (mission_state == "POWERED ASCENT" and mission_time > 120):
                    mission_time += 1
                    parachute_deployed = True
                    stage = "PARACHUTE_DESCENT"
                    raw_altitude = max(0.0, raw_altitude - 0.15)
                    raw_velocity = 25.0
                    pitch = 0.0

            kalman.predict()
            filtered_alt, filtered_vel = kalman.update(raw_altitude)

            seq_counter = (seq_counter + 1) % 16384
            payload = struct.pack(">fffff", filtered_alt, filtered_vel, pitch if 'pitch' in locals() else 90.0, lat, lon)
            ccsds_hex = build_ccsds_packet(apid=0x01A, seq_count=seq_counter, payload_bytes=payload).hex().upper()

            latest_telemetry = {
                "mission_id": current_mission_id,
                "time": mission_time,
                "altitude": round(filtered_alt, 2),
                "velocity": round(filtered_vel, 1),
                "pitch": round(pitch if 'pitch' in locals() else 90.0, 1),
                "status": mission_state,
                "stage": stage,
                "parachute": parachute_deployed,
                "dsn_station": calculate_active_ground_station(lat, lon),
                "ccsds_frame": ccsds_hex[:32] + "...",
                "lat": lat,
                "lon": lon
            }

            if database.is_connected and mission_state != "STANDBY":
                try:
                    query = telemetry_table.insert().values(mission_id=current_mission_id, mission_time=mission_time, altitude=filtered_alt, velocity=filtered_vel, status=mission_state)
                    await database.execute(query)
                except Exception:
                    pass

            await websocket.send_text(json.dumps(latest_telemetry))
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        pass

@app.get("/api/missions")
async def get_missions_list():
    if not database.is_connected:
        return {"missions": []}
    query = sqlalchemy.select(telemetry_table.c.mission_id).distinct()
    rows = await database.fetch_all(query)
    return {"missions": [row["mission_id"] for row in rows]}

@app.get("/api/stats")
async def get_mission_stats():
    if not database.is_connected:
        return {"error": "BD Offline"}
    query = telemetry_table.select()
    rows = await database.fetch_all(query)
    if not rows:
        return {"max_altitude": 0.0, "max_velocity": 0.0, "total_records": 0}
    return {"max_altitude": round(max(r["altitude"] for r in rows), 2), "max_velocity": round(max(r["velocity"] for r in rows), 1), "total_records": len(rows)}

@app.get("/export/pdf/{mission_id}")
async def export_mission_pdf(mission_id: int):
    if not database.is_connected:
        return {"error": "BD Offline"}
    query = telemetry_table.select().where(telemetry_table.c.mission_id == mission_id)
    rows = await database.fetch_all(query)
    if not rows:
        return {"error": "Sin datos"}
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"INFORME DE MISIÓN NASA ODYSSEY-1 [ID #{mission_id}]", styles['Heading1']))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"<b>Registros Guardados:</b> {len(rows)} puntos de telemetría", styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=mission_{mission_id}_report.pdf"})

class AIQueryRequest(BaseModel):
    prompt: str

@app.post("/ai/query")
async def ai_interactive_query(request: AIQueryRequest):
    if not ai_client:
        return {"error": "Gemini API Key no configurada"}
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=f"[Contexto ODYSSEY-1 Gemelo Digital] {request.prompt}")
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}
