import sqlite3
from fastapi import APIRouter

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
