from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import json
import socket
import math
import hashlib
import hmac

app = FastAPI(title="ODYSSEY-1 Real HIL FSW Core", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/web", StaticFiles(directory=os.path.join(BASE_DIR, "web")), name="web")

fsw_state = {
    "time": 0,
    "status": "HIL HARDWARE STANDBY",
    "altitude": 0.0,
    "velocity": 0.0,
    "lat": 28.5721,
    "lon": -80.6480,
    "pitch": 0.0,
    "yaw": 0.0,
    "roll": 0.0,
    "rw_momentum": [0.45, 0.15, 0.23],
    "crc_valid": True,
    "clock_drift_ms": 0.12,
    "source": "SIMULATION"
}

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT))
    udp_socket.setblocking(False)
except Exception:
    udp_socket = None

def check_hardware_udp():
    if not udp_socket:
        return False
    try:
        data, addr = udp_socket.recvfrom(1024)
        packet = json.loads(data.decode('utf-8'))
        fsw_state["altitude"] = packet.get("alt", fsw_state["altitude"])
        fsw_state["velocity"] = packet.get("vel", fsw_state["velocity"])
        fsw_state["pitch"] = packet.get("pitch", fsw_state["pitch"])
        fsw_state["roll"] = packet.get("roll", fsw_state["roll"])
        fsw_state["status"] = "HIL HARDWARE LINK ACTIVE (ESP32)"
        fsw_state["source"] = f"PHYSICAL HW ({addr[0]})"
        return True
    except (BlockingIOError, socket.error, json.JSONDecodeError, AttributeError):
        return False

@app.get("/")
def read_root():
    return {"system": "ODYSSEY-1 HIL Bridge", "status": "active", "udp_port": UDP_PORT}

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(BASE_DIR, "web", "flight_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Dashboard no encontrado</h1></body></html>"

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        t = 0
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.05)
                if isinstance(msg, dict) and msg.get("command") == "LAUNCH":
                    fsw_state["status"] = "ACTIVE FLIGHT (HIL & J2)"
            except (asyncio.TimeoutError, Exception):
                pass

            t += 1
            fsw_state["time"] = t

            hw_received = check_hardware_udp()
            if not hw_received and fsw_state["source"] == "SIMULATION":
                fsw_state["altitude"] = round(400.0 + math.sin(t * 0.1) * 3.0, 2)
                fsw_state["velocity"] = round(7668.5 + math.cos(t * 0.1) * 1.2, 2)
                fsw_state["lat"] = round(28.5721 + math.sin(t * 0.05) * 10.0, 4)
                fsw_state["lon"] = round(-80.6480 + (t * 0.1) % 360 - 180, 4)

            payload_bytes = f"ALT:{fsw_state['altitude']}|VEL:{fsw_state['velocity']}|T:{t}".encode('utf-8')
            crc = hmac.new(b"ODYSSEY_HIL_KEY", payload_bytes, hashlib.sha256).hexdigest()[:4].upper()

            telemetry_packet = {
                "time": t,
                "altitude": fsw_state["altitude"],
                "velocity": fsw_state["velocity"],
                "status": fsw_state["status"],
                "lat": fsw_state["lat"],
                "lon": fsw_state["lon"],
                "pitch": fsw_state["pitch"] if fsw_state["source"] != "SIMULATION" else round(math.sin(t * 0.05) * 4.0, 2),
                "yaw": 0.0,
                "roll": fsw_state["roll"] if fsw_state["source"] != "SIMULATION" else round((t * 1.0) % 360, 2),
                "rw_momentum": fsw_state["rw_momentum"],
                "crc_valid": True,
                "clock_drift_ms": 0.15,
                "ccsds_frame": f"01AF0008{payload_bytes.hex().upper()[:20]}...{crc}",
                "dsn_station": "Madrid (DSS-63) [HIL MODE]",
                "blackout_status": f"SOURCE: {fsw_state['source']}"
            }

            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
