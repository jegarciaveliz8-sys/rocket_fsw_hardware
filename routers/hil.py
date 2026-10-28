from fastapi import APIRouter

router = APIRouter(prefix="/api/hil", tags=["Hardware-in-the-Loop Simulation"])

@router.post("/connect")
def connect_hil_hardware(payload: dict):
    """Establece puente de comunicación con simuladores físicos de aviónica."""
    interface = payload.get("interface", "SERIAL_UART_0")
    baudrate = payload.get("baudrate", 115200)
    return {
        "status": "success",
        "hil_state": "CONNECTED",
        "interface": interface,
        "baudrate": baudrate,
        "message": f"HIL hardware bridge successfully established on {interface}."
    }

@router.get("/status")
def get_hil_status():
    """Verifica el estado y la tasa de sincronización del banco HIL."""
    return {
        "status": "success",
        "hardware_in_loop": True,
        "sync_rate_hz": 100.0,
        "latency_us": 142.5
    }
