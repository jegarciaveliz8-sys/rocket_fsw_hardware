from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import math
import hashlib
import hmac

from routers import mission_api, subsystems_api

app = FastAPI(title="ODYSSEY-1 Modular Mission Control Center", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(BASE_DIR, "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir), name="web")

app.include_router(mission_api.router)
app.include_router(subsystems_api.router)

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
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.05)
                if isinstance(msg, dict) and msg.get("command") == "LAUNCH":
                    mission_api.fsw_state["status"] = "POWERED ASCENT"
            except (asyncio.TimeoutError, Exception):
                pass

            t += 1
            mission_api.fsw_state["time"] = t
            mission_api.fsw_state["altitude"] = round(400.0 + math.sin(t * 0.1) * 3.0, 2)
            mission_api.fsw_state["velocity"] = round(7668.5 + math.cos(t * 0.1) * 1.2, 2)

            payload_bytes = f"ALT:{mission_api.fsw_state['altitude']}|VEL:{mission_api.fsw_state['velocity']}|T:{t}".encode('utf-8')
            crc = hmac.new(b"ODYSSEY_HIL_KEY", payload_bytes, hashlib.sha256).hexdigest()[:4].upper()

            telemetry_packet = {
                "time": t,
                "timestamp": t,
                "altitude": mission_api.fsw_state["altitude"],
                "velocity": mission_api.fsw_state["velocity"],
                "speed": mission_api.fsw_state["velocity"],
                "payload": "active",
                "failover": "ready",
                "status": mission_api.fsw_state["status"],
                "lat": mission_api.fsw_state["lat"],
                "lon": mission_api.fsw_state["lon"],
                "pitch": round(math.sin(t * 0.05) * 4.0, 2),
                "yaw": 0.0,
                "roll": round((t * 1.0) % 360, 2),
                "rw_momentum": mission_api.fsw_state["rw_momentum"],
                "crc_valid": True,
                "clock_drift_ms": 0.15,
                "ccsds_frame": f"01AF0008{payload_bytes.hex().upper()[:20]}...{crc}",
                "dsn_station": "Madrid (DSS-63) [MODULAR HIL]",
                "blackout_status": "SOURCE: SIMULATION"
            }

            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
