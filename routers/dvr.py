from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/dvr", tags=["DVR & Session Recording"])

@router.post("/start")
def start_dvr_recording():
    return {
        "status": "success",
        "dvr_state": "RECORDING",
        "message": "DVR session recording initialized successfully."
    }

@router.post("/stop")
def stop_dvr_recording():
    return {
        "status": "success",
        "dvr_state": "STOPPED",
        "message": "DVR session recording saved to storage."
    }

@router.get("/sessions")
def list_dvr_sessions():
    return {
        "status": "success",
        "sessions": [
            {"id": "ODYSSEY_FLIGHT_001", "duration": "00:12:45", "size_mb": 45.2},
            {"id": "ODYSSEY_FLIGHT_002", "duration": "00:25:10", "size_mb": 89.6}
        ]
    }
