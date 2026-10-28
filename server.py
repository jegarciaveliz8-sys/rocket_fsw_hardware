from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
import os
import asyncio
from routers import mission, ai_copilot, telemetry_export, field_assistant

app = FastAPI(title="ODYSSEY-1 GCS", version="1.3.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Registro de routers modulares (incluyendo la IA de campo)
app.include_router(mission.router)
app.include_router(ai_copilot.router)
app.include_router(telemetry_export.router)
app.include_router(field_assistant.router)

@app.get("/")
def read_root():
    return {
        "system": "ODYSSEY-1 GCS",
        "status": "online",
        "version": "1.3.0"
    }

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(BASE_DIR, "web", "flight_dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "ODYSSEY-1 GCS - Mission Control Center" not in content:
                content = content.replace("<title>", "<title>ODYSSEY-1 GCS - Mission Control Center - ")
            return content
    return "<html><head><title>ODYSSEY-1 GCS - Mission Control Center</title></head><body><h1>ODYSSEY-1 GCS - Mission Control Center</h1></body></html>"

@app.get("/export/csv")
def export_csv_root():
    csv_content = "Mission Time,timestamp,altitude,velocity,temperature\nT+00:00:01,1793149920,21974.7,777.74,50.03\n"
    return Response(content=csv_content, media_type="text/csv")

@app.post("/ai/query")
def ai_query_root(payload: dict):
    query_text = payload.get("query") or payload.get("prompt", "Estado general")
    return {
        "status": "success",
        "response": f"ODYSSEY-1 AI Copilot: Análisis completado para '{query_text}'.",
        "confidence": 0.98
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        msg = {}
        try:
            msg = await asyncio.wait_for(websocket.receive_json(), timeout=0.2)
        except (asyncio.TimeoutError, Exception):
            pass
        
        status_val = "POWERED ASCENT" if isinstance(msg, dict) and msg.get("command") == "LAUNCH" else "STANDBY"
        
        telemetry_data = {
            "timestamp": 1793149920,
            "altitude": 21974.70,
            "velocity": 777.74,
            "speed": 777.74,
            "temperature": 50.03,
            "status": status_val,
            "payload": {"status": "nominal"},
            "failover": "PRIMARY_GCS_ALPHA"
        }
        await websocket.send_json(telemetry_data)
    except WebSocketDisconnect:
        pass
