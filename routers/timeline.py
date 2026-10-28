from fastapi import APIRouter

router = APIRouter(prefix="/api/timeline", tags=["Launch Timeline & Countdown"])

@router.get("/status")
def get_timeline_status():
    """Devuelve el estado de la cuenta regresiva (T-minus) y eventos automáticos."""
    return {
        "status": "success",
        "countdown_state": "HOLD",
        "t_minus_seconds": -300,
        "scheduled_events": [
            {"event": "ARM_PYROS", "t_offset_sec": -60, "status": "PENDING"},
            {"event": "INTERNAL_POWER", "t_offset_sec": -30, "status": "PENDING"},
            {"event": "IGNITION", "t_offset_sec": 0, "status": "ARMED"}
        ]
    }

@router.post("/hold")
def hold_countdown():
    """Pone la cuenta regresiva de lanzamiento en modo de espera (HOLD)."""
    return {
        "status": "success",
        "countdown_state": "HOLD",
        "message": "Launch sequence placed on HOLD by flight director."
    }
