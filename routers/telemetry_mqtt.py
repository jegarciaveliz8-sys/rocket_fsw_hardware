import json
import sqlite3
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/api/telemetry", tags=["Realtime HIL"])

# Lista de WebSockets conectados para broadcast en vivo
active_connections: list[WebSocket] = []

@router.websocket("/ws/live")
async def live_telemetry_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Procesar datos en tiempo real si es necesario
    except WebSocketDisconnect:
        active_connections.remove(websocket)
