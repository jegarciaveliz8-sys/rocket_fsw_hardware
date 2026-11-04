from fastapi import APIRouter
from pydantic import BaseModel
import time

router = APIRouter(prefix="/api/fdir", tags=["FDIR & Fault Management"])

# Estado interno del FDIR autónomo y mitigaciones activas
fdir_autonomous_state = {
    "power_save_mode": False,
    "rtl_triggered": False,
    "active_faults": [],
    "recovery_actions_taken": []
}

class FDIROverrideRequest(BaseModel, extra="allow"):
    subsystem: str = "GENERAL"
    action: str = "ISOLATE"

@router.get("/state-vector")
def get_fdir_state_vector():
    """Devuelve el vector de estado FDIR (Fault Detection, Isolation, and Recovery)."""
    return {
        "status": "nominal",
        "system_health": "GREEN" if not fdir_autonomous_state["active_faults"] else "WARNING",
        "fault_detected": len(fdir_autonomous_state["active_faults"]) > 0,
        "active_faults": fdir_autonomous_state["active_faults"],
        "subsystems": {
            "imu_ekf": {"state": "HEALTHY", "error_code": 0x00, "confidence": 0.99},
            "power_distribution": {"state": "WARNING" if fdir_autonomous_state["power_save_mode"] else "HEALTHY", "voltage_v": 28.4, "current_a": 12.5},
            "comms_link": {"state": "HEALTHY", "packet_loss_pct": 0.02, "rssi_dbm": -65},
            "actuators_gimbal": {"state": "HEALTHY", "thermal_c": 42.1}
        },
        "recovery_actions_triggered": len(fdir_autonomous_state["recovery_actions_taken"]),
        "failover_active": fdir_autonomous_state["rtl_triggered"]
    }

@router.post("/override")
def trigger_fdir_override(payload: dict):
    """Permite aislar o reiniciar un subsistema de forma remota en caso de anomalía."""
    subsystem = payload.get("subsystem", "GENERAL")
    action = payload.get("action", "ISOLATE")
    fdir_autonomous_state["recovery_actions_taken"].append(f"MANUAL_OVERRIDE: {action} on {subsystem}")
    return {
        "status": "success",
        "fdir_action": action,
        "target_subsystem": subsystem,
        "message": f"Subsistema '{subsystem}' procesado por política FDIR: {action}"
    }

def evaluate_telemetry_fdir(telemetry_packet: dict) -> dict:
    """
    Motor autónomo en tiempo real evaluado por el bucle del WebSocket.
    Detecta anomalías y ejecuta recuperación dinámica sin intervención humana.
    """
    faults = []
    
    battery = telemetry_packet.get("battery_pct", 100.0)
    pressure = telemetry_packet.get("chamber_pressure", 15.4)
    snr = telemetry_packet.get("snr", 25.0)
    
    # 1. Detección de batería crítica (< 18%) -> Activar Modo Ahorro
    if battery < 18.0 and not fdir_autonomous_state["power_save_mode"]:
        faults.append("CRITICAL_BATTERY_DROP")
        fdir_autonomous_state["power_save_mode"] = True
        fdir_autonomous_state["recovery_actions_taken"].append("AUTONOMOUS: Power-Save Mode engaged.")

    # 2. Detección de degradación de enlace RF (< 5 dB) -> Activar RTL
    if snr < 5.0 and not fdir_autonomous_state["rtl_triggered"]:
        faults.append("RF_LINK_DEGRADATION")
        fdir_autonomous_state["rtl_triggered"] = True
        fdir_autonomous_state["recovery_actions_taken"].append("AUTONOMOUS: Return-to-Launch (RTL) triggered.")

    # 3. Sobrepresión en cámara (> 17.5 PSI)
    if pressure > 17.5:
        faults.append("CHAMBER_OVERPRESSURE")

    fdir_autonomous_state["active_faults"] = faults

    # Inyectar métricas FDIR en el paquete de telemetría que viaja al cliente/dashboard
    telemetry_packet["fdir_status"] = "RECOVERY_IN_PROGRESS" if faults else "NOMINAL"
    telemetry_packet["fdir_faults"] = faults
    telemetry_packet["power_save_mode"] = fdir_autonomous_state["power_save_mode"]
    
    return telemetry_packet
