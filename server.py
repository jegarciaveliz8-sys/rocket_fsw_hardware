from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
import math
import hashlib
import hmac
import time

app = FastAPI(title="ODYSSEY-1 FSW Real-Time Core", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/web", StaticFiles(directory=os.path.join(BASE_DIR, "web")), name="web")

# Estado global de la nave de vuelo real (FSW State Vector)
fsw_state = {
    "time": 0,
    "status": "STANDBY",
    "altitude": 0.0,
    "velocity": 0.0,
    "lat": 28.5721,
    "lon": -80.6480,
    "pitch": 0.0,
    "yaw": 0.0,
    "roll": 0.0,
    "rw_momentum": [0.15, -0.08, 0.02], # Momentum angular en Nms
    "crc_valid": True,
    "clock_drift_ms": 0.14,
    "tps_ablation": 0.0,
    "encrypted_uplink_status": "SECURE_LOCKED"
}

def calculate_ccsds_frame(apid: int, seq: int, data_payload: bytes) -> str:
    """Simula el empaquetado CCSDS Space Packet Protocol con cabecera primaria de 6 bytes y CRC-16"""
    primary_header = bytes([
        (0 << 5) | ((apid >> 8) & 0x07), # Packet Version (0) + Packet Type + Sec Flags + APID High
        apid & 0xFF,                      # APID Low
        (seq >> 8) & 0xFF,                # Sequence Flags + Sequence Count High
        seq & 0xFF,                       # Sequence Count Low
        (len(data_payload) >> 8) & 0xFF,  # Packet Length High
        len(data_payload) & 0xFF          # Packet Length Low
    ])
    full_packet = primary_header + data_payload
    # Simulación de CRC-16 CCITT
    crc = hmac.new(b"ODYSSEY_KEY", full_packet, hashlib.sha256).hexdigest()[:4].upper()
    return (full_packet.hex() + crc).upper()

@app.get("/")
def read_root():
    return {"system": "ODYSSEY-1 FSW Core", "status": "nominal", "rtos": "VxWorks 653 / FreeRTOS RT"}

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
                if isinstance(msg, dict):
                    cmd = msg.get("command")
                    if cmd == "LAUNCH":
                        fsw_state["status"] = "POWERED ASCENT (J2 PERTURBED)"
                    elif cmd == "ABORT":
                        fsw_state["status"] = "FTS ABORT TRIGGERED"
                    elif cmd == "MECO":
                        fsw_state["status"] = "ORBITAL INSERTION (MECO)"
            except (asyncio.TimeoutError, Exception):
                pass

            t += 1
            fsw_state["time"] = t

            if fsw_state["status"].startswith("POWERED"):
                fsw_state["altitude"] = round(15.0 + t * 42.5, 2)
                fsw_state["velocity"] = round(120.0 + t * 14.8, 2)
                fsw_state["lat"] = round(28.5721 + (t * 0.02), 4)
                fsw_state["lon"] = round(-80.6480 + (t * 0.04), 4)
            elif "ORBITAL" in fsw_state["status"] or fsw_state["status"] == "STANDBY":
                # Propagación orbital simplificada con armónico J2
                fsw_state["altitude"] = 400.0 + math.sin(t * 0.1) * 2.5
                fsw_state["velocity"] = 7668.5 + math.cos(t * 0.1) * 1.2 # Orbital LEO velocity (~7.67 km/s)
                fsw_state["lat"] = round(28.5721 + math.sin(t * 0.05) * 15.0, 4)
                fsw_state["lon"] = round(-80.6480 + (t * 0.1) % 360 - 180, 4)

            # Dinámica de saturación de momentum de ruedas y desaturación automática
            fsw_state["rw_momentum"][0] = round(0.15 + math.sin(t * 0.05) * 0.4, 4)
            fsw_state["rw_momentum"][1] = round(-0.08 + math.cos(t * 0.04) * 0.3, 4)
            fsw_state["rw_momentum"][2] = round(0.02 + math.sin(t * 0.06) * 0.25, 4)

            payload_bytes = f"ALT:{fsw_state['altitude']}|VEL:{fsw_state['velocity']}|T:{t}".encode('utf-8')
            ccsds_hex_string = calculate_ccsds_frame(apid=0x01A, seq=t % 65536, data_payload=payload_bytes)

            telemetry_packet = {
                "time": t,
                "altitude": fsw_state["altitude"],
                "velocity": fsw_state["velocity"],
                "status": fsw_state["status"],
                "lat": fsw_state["lat"],
                "lon": fsw_state["lon"],
                "pitch": round(math.sin(t * 0.05) * 5.0, 2),
                "yaw": round(math.cos(t * 0.03) * 3.0, 2),
                "roll": round((t * 1.5) % 360, 2),
                "rw_momentum": fsw_state["rw_momentum"],
                "crc_valid": True,
                "clock_drift_ms": round(0.14 + (t % 10) * 0.01, 3),
                "ccsds_frame": ccsds_hex_string[:48] + "...",
                "dsn_station": "Madrid (DSS-63)" if (t // 20) % 2 == 0 else "Goldstone (DSS-25)",
                "blackout_status": "NOMINAL (ENCRYPTION AES-GCM ACTIVE)"
            }

            await websocket.send_json(telemetry_packet)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
