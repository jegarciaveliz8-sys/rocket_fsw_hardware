from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from routers import (
    mission, ai_copilot, telemetry_export, field_assistant, 
    dvr, reports, fdir, tactical, monte_carlo, security, 
    payload_science, swarm, timeseries, hil, video_feed, 
    timeline, weather, replay, auth, audit, network_sim, orbit_math
)

app = FastAPI(title="ODYSSEY-1 GCS", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Servir archivos estáticos de la carpeta web (CSS, JS)
app.mount("/web", StaticFiles(directory=os.path.join(BASE_DIR, "web")), name="web")

# Registro integral de los 22 subsistemas
app.include_router(mission.router)
app.include_router(ai_copilot.router)
app.include_router(telemetry_export.router)
app.include_router(field_assistant.router)
app.include_router(dvr.router)
app.include_router(reports.router)
app.include_router(fdir.router)
app.include_router(tactical.router)
app.include_router(monte_carlo.router)
app.include_router(security.router)
app.include_router(payload_science.router)
app.include_router(swarm.router)
app.include_router(timeseries.router)
app.include_router(hil.router)
app.include_router(video_feed.router)
app.include_router(timeline.router)
app.include_router(weather.router)
app.include_router(replay.router)
app.include_router(auth.router)
app.include_router(audit.router)
app.include_router(network_sim.router)
app.include_router(orbit_math.router)

@app.get("/")
def read_root():
    return {"system": "ODYSSEY-1 GCS", "status": "online", "version": "1.3.0"}

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(BASE_DIR, "web", "flight_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>Dashboard HTML no encontrado en web/flight_dashboard.html</h1></body></html>"

@app.get("/api/missions")
def get_missions():
    return {"missions": [1, 2, 3]}

@app.get("/export/pdf/{mission_id}")
def export_pdf(mission_id: int):
    return Response(content=f"PDF Report for Mission #{mission_id}", media_type="application/pdf")

@app.post("/ai/query")
def ai_query(payload: dict):
    prompt = payload.get("prompt", "Estado general")
    return {"response": f"ODYSSEY-1 AI Copilot: Análisis nominal para '{prompt}'."}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        t = 0
        current_status = "STANDBY"
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if isinstance(msg, dict):
                    cmd = msg.get("command")
                    if cmd == "LAUNCH":
                        current_status = "POWERED ASCENT"
                    elif cmd in ["ABORT", "RESET", "MECO"]:
                        current_status = cmd
            except (asyncio.TimeoutError, Exception):
                pass
            
            t += 1
            telemetry_data = {
                "time": t,
                "mission_id": 1,
                "timestamp": 1793149920 + t,
                "altitude": round(21974.70 + (t * 2.5), 2),
                "velocity": round(777.74 + (t * 5.0), 2),
                "speed": round(777.74 + (t * 5.0), 2),
                "pressure": 15.4,
                "temperature": round(50.03 + (t * 0.1), 2),
                "status": current_status,
                "dsn_station": "Madrid (DSS-63)" if (t // 15) % 2 == 0 else "Cape Canaveral",
                "blackout_status": "BLACKOUT ATMOSFÉRICO" if 10 <= t <= 25 else "NOMINAL (LINK OK)",
                "orbit_a": 6371.0,
                "orbit_e": 0.0000,
                "orbit_i": 28.5,
                "injected_fault": "NONE",
                "fdir_action": "NOMINAL",
                "ccsds_frame": f"081AC0000{t:04X}C4F2...",
                "pitch": round(15.0 * max(0, 1 - (t/50)), 2),
                "yaw": 0.0,
                "roll": round((t * 3) % 360, 2),
                "lat": round(28.5721 + (t * 0.05), 4),
                "lon": round(-80.6480 + (t * 0.1), 4),
                "payload": {"status": "nominal"},
                "failover": "PRIMARY_GCS_ALPHA"
            }
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
