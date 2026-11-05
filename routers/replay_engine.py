import sqlite3
import asyncio
import csv
import io
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/replay", tags=["Flight Replay"])

@router.get("/sessions")
def get_recorded_sessions():
    """Obtiene un resumen de los paquetes grabados disponibles para reproducción."""
    conn = sqlite3.connect("odyssey_telemetry.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, flight_time, altitude, velocity, status FROM flight_logs ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "status": "success",
        "total_frames": len(rows),
        "frames": rows
    }

@router.get("/anomalies")
def get_mission_anomalies():
    """Filtra y devuelve todos los paquetes que contengan eventos FDIR o alertas críticas."""
    conn = sqlite3.connect("odyssey_telemetry.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, flight_time, status, altitude FROM flight_logs WHERE status LIKE '%ALERT%' OR status LIKE '%BREACH%' OR status LIKE '%ERROR%' ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {
        "status": "success",
        "total_anomalies": len(rows),
        "anomalies": rows
    }

@router.websocket("/ws/stream")
async def websocket_replay_stream(websocket: WebSocket):
    """Transmite los paquetes de telemetría históricos segundo a segundo."""
    await websocket.accept()
    conn = sqlite3.connect("odyssey_telemetry.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flight_logs ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    try:
        for row in rows:
            await websocket.send_json(dict(row))
            await asyncio.sleep(1)
        await websocket.send_json({"status": "REPLAY_COMPLETE"})
    except WebSocketDisconnect:
        pass

@router.get("/export/csv")
def export_mission_logs():
    """Exporta todos los registros de vuelo en formato CSV para análisis externo."""
    conn = sqlite3.connect("odyssey_telemetry.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flight_logs ORDER BY id ASC")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(column_names)
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=odyssey_flight_audit_report.csv"}
    )
