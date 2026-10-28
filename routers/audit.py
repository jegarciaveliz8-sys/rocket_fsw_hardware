from fastapi import APIRouter

router = APIRouter(prefix="/api/audit", tags=["Mission Audit Logs"])

@router.get("/logs")
def get_mission_audit_trail(limit: int = 20):
    """Devuelve el registro inmutable de auditoría forense de la misión."""
    return {
        "status": "success",
        "total_events": 3,
        "audit_logs": [
            {"timestamp": 1793149900, "operator": "flight_director", "action": "ARM_SYSTEMS", "status": "AUTHORIZED"},
            {"timestamp": 1793149915, "operator": "telemetry_eng", "action": "FDIR_OVERRIDE_IMU", "status": "SUCCESS"},
            {"timestamp": 1793149920, "operator": "flight_director", "action": "TRIGGER_LAUNCH", "status": "EXECUTED"}
        ]
    }
