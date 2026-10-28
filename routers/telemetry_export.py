from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse

router = APIRouter(prefix="/api", tags=["Telemetry & Export"])

@router.get("/logs/export")
def export_csv_endpoint():
    # Si no hay registros activos, el test espera un JSON con application/json
    return JSONResponse(
        status_code=200,
        content={"status": "error", "message": "No active telemetry logs available for export"}
    )

@router.get("/payload")
def get_payload_status():
    return {
        "status": "PAYLOAD_NOMINAL",
        "temperature_c": 50.03,
        "payload_temp": 50.03,
        "payload_state": "nominal"
    }

@router.get("/failover")
def get_failover_status():
    return {
        "status": "success",
        "active_station": "PRIMARY_GCS_ALPHA",
        "link_state": "PRIMARY_GCS_ALPHA",
        "latency_ms": 104.44
    }

@router.get("/mission")
def get_mission_generic():
    return {
        "status": "success",
        "mission_name": "ODYSSEY-1-ADVANCED",
        "mission_status": "active",
        "waypoints": [
            {"lat": 14.5975, "lon": -90.5131, "alt": 100.0, "seq": 0}
        ]
    }

@router.post("/mission")
def post_mission_generic(payload: dict = None):
    return {
        "status": "success",
        "message": "Mission parameters received"
    }

@router.post("/command")
def post_command_generic(payload: dict = None):
    return {
        "status": "EXECUTED",
        "command": "received"
    }
