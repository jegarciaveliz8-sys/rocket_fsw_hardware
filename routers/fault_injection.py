from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/faults", tags=["Fault Injection"])

# Estado actual de las fallas inyectadas
fault_state = {
    "rf_blackout": False,
    "gps_failure": False,
    "low_battery_spike": False
}

class FaultRequest(BaseModel):
    fault_type: str
    active: bool

@router.post("/toggle")
async def toggle_fault(payload: FaultRequest):
    ftype = payload.fault_type
    if ftype in fault_state:
        fault_state[ftype] = payload.active
        print(f"⚠️ [FAULT INJECTION] Falla '{ftype}' configurada a: {payload.active}")
        return {"status": "SUCCESS", "fault": ftype, "active": payload.active}
    return {"status": "ERROR", "message": "Tipo de falla no reconocido"}
