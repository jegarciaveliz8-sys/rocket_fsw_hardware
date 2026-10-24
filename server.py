import os
import sqlite3
import random
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "flight_recorder.db")

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ODYSSEY-1 GCS Enterprise", version="1.1.0", lifespan=lifespan)

class PayloadProcessor:
    def ingest_telemetry(self):
        return {
            "temperature_c": round(random.uniform(20.0, 85.5), 2),
            "radiation_msv": round(random.uniform(0.05, 1.2), 4),
            "internal_pressure_kpa": round(random.uniform(100.0, 101.3), 2),
            "status": "PAYLOAD_NOMINAL"
        }

class MissionParser:
    def __init__(self, file_path="mission_plan.json"):
        self.file_path = os.path.join(BASE_DIR, file_path)

    def load_mission(self):
        if not os.path.exists(self.file_path):
            mission = {
                "mission_name": "ODYSSEY-1-ADVANCED",
                "waypoints": [
                    {"id": 1, "lat": 14.7883, "lon": -90.1988, "alt_target": 1000},
                    {"id": 2, "lat": 14.8000, "lon": -90.2100, "alt_target": 15000},
                    {"id": 3, "lat": 14.8500, "lon": -90.2500, "alt_target": 45000}
                ]
            }
            with open(self.file_path, "w") as f:
                json.dump(mission, f, indent=4)
        with open(self.file_path, "r") as f:
            return json.load(f)

class StationFailoverManager:
    def __init__(self):
        self.active_station = "PRIMARY_GCS_ALPHA"

    def check_link_health(self):
        latency = random.uniform(10, 200)
        if latency > 180:
            self.active_station = "BACKUP_GCS_BETA"
        else:
            self.active_station = "PRIMARY_GCS_ALPHA"
        return {"active_station": self.active_station, "latency_ms": round(latency, 2)}

payload_mgr = PayloadProcessor()
mission_mgr = MissionParser()
failover_mgr = StationFailoverManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {"status": "ONLINE", "system": "ODYSSEY-1 GCS", "version": "1.1.0"}

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return "<h1>Dashboard HTML no encontrado</h1>"

@app.get("/api/payload")
def get_payload_data():
    return payload_mgr.ingest_telemetry()

@app.get("/api/mission")
def get_mission_plan():
    return mission_mgr.load_mission()

@app.get("/api/failover")
def get_failover_status():
    return failover_mgr.check_link_health()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            telemetry_packet = {
                "altitude": round(random.uniform(0, 45000), 2),
                "speed": round(random.uniform(0, 1200), 2),
                "payload": payload_mgr.ingest_telemetry(),
                "failover": failover_mgr.check_link_health()
            }
            await websocket.send_text(json.dumps(telemetry_packet))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
