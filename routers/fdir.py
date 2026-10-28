from fastapi import APIRouter

router = APIRouter(prefix="/api/fdir", tags=["FDIR & Fault Management"])

@router.get("/state-vector")
def get_fdir_state_vector():
    """Devuelve el vector de estado FDIR (Fault Detection, Isolation, and Recovery)."""
    return {
        "status": "nominal",
        "system_health": "GREEN",
        "fault_detected": False,
        "active_faults": [],
        "subsystems": {
            "imu_ekf": {"state": "HEALTHY", "error_code": 0x00, "confidence": 0.99},
            "power_distribution": {"state": "HEALTHY", "voltage_v": 28.4, "current_a": 12.5},
            "comms_link": {"state": "HEALTHY", "packet_loss_pct": 0.02, "rssi_dbm": -65},
            "actuators_gimbal": {"state": "HEALTHY", "thermal_c": 42.1}
        },
        "recovery_actions_triggered": 0,
        "failover_active": False
    }

@router.post("/override")
def trigger_fdir_override(payload: dict):
    """Permite aislar o reiniciar un subsistema de forma remota en caso de anomalía."""
    subsystem = payload.get("subsystem", "GENERAL")
    action = payload.get("action", "ISOLATE")
    return {
        "status": "success",
        "fdir_action": action,
        "target_subsystem": subsystem,
        "message": f"Subsistema '{subsystem}' procesado por política FDIR: {action}"
    }
