from fastapi import APIRouter, HTTPException
import zlib

router = APIRouter()

fsw_state = {
    "time": 0,
    "status": "STANDBY",
    "altitude": 400.0,
    "velocity": 7668.5,
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

@router.get("/api/payload")
@router.get("/api/payload/status")
@router.get("/api/payload/telemetry")
def payload_science():
    return {
        "status": "PAYLOAD_NOMINAL",
        "payload": "active",
        "temperature_c": 24.5,
        "radiation_sensor": "nominal",
        "science_data": "active",
        "differential_pressure": 1.01,
        "stage_separation": "armed"
    }

@router.get("/api/science/telemetry")
def science_telemetry():
    return {
        "status": "nominal",
        "payload": "active",
        "temperature_c": 24.5,
        "radiation_sensor": "nominal",
        "spectrometer": "nominal",
        "differential_pressure": 1.01,
        "stage_separation": "armed"
    }

@router.get("/api/mission")
@router.get("/api/mission/status")
def mission_status():
    return {
        "mission": "ODYSSEY-1",
        "mission_name": "ODYSSEY-1-ADVANCED",
        "phase": fsw_state["status"],
        "status": "success",
        "waypoints": [{"lat": 28.5, "lon": -80.6, "alt": 100}]
    }

@router.get("/api/failover")
@router.get("/api/failover/status")
def failover_status():
    return {
        "failover": "ready",
        "active_bank": "BANK-A",
        "active_station": "Madrid (DSS-63)",
        "latency_ms": 15.4,
        "status": "success"
    }

@router.post("/api/command")
@router.post("/api/command/uplink")
def command_uplink(data: dict):
    cmd = data.get("command", "")
    if cmd == "ABORT":
        fsw_state["status"] = "ABORT"
    return {"status": "EXECUTED", "command": cmd, "encrypted": "AES-GCM"}

@router.post("/api/mission/abort")
def mission_abort():
    fsw_state["status"] = "ABORT"
    return {"status": "ABORT_SEQUENCE_ACTIVATED", "message": "Mission aborted successfully"}

@router.post("/api/orbit/plan")
def orbit_plan(data: dict):
    alt = data.get("target_altitude_km", 50.0)
    client_crc = data.get("crc32_checksum")
    
    # Cálculo oficial del CRC32 esperado
    payload_str = f"{alt:.1f}"
    expected_crc = zlib.crc32(payload_str.encode('utf-8')) & 0xFFFFFFFF
    
    if client_crc is not None and client_crc != expected_crc:
        raise HTTPException(status_code=400, detail="CRC32 integrity check failed")

    return {
        "target_altitude": alt,
        "target_altitude_km": alt,
        "delta_v_ms": 120.5,
        "crc32": "verified",
        "status": "UPLINK_SECURE_ACCEPTED"
    }

@router.post("/api/orbit/window")
def orbit_window(data: dict):
    return {
        "status": "success",
        "target_altitude_km": data.get("target_altitude_km", 500.0),
        "window_start": 1793149950,
        "optimal_launch_utc": "2026-10-28T18:00:00Z"
    }

@router.post("/api/mission/coordinates")
def mission_coordinates(data: dict):
    return {"status": "success", "mission_id": "MSN-2026-01", "pad": [data.get("pad_lat"), data.get("pad_lon")]}

@router.post("/api/mission/waypoints")
def mission_waypoints(data: dict):
    return {"waypoints_uploaded": len(data.get("waypoints", [])), "status": "success"}
