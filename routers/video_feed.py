from fastapi import APIRouter

router = APIRouter(prefix="/api/video", tags=["Live Video & Optics"])

@router.get("/streams")
def list_video_streams():
    """Devuelve las fuentes de video activas de la cofia y la carga útil."""
    return {
        "status": "success",
        "streams": [
            {"id": "CAM_NOSE_CONE", "status": "ACTIVE", "codec": "H.264", "fps": 60, "resolution": "1080p"},
            {"id": "CAM_PAYLOAD_BAY", "status": "ACTIVE", "codec": "H.265", "fps": 30, "resolution": "4K"}
        ]
    }

@router.post("/ptz")
def control_camera_ptz(payload: dict):
    """Controla paneo, inclinación y zoom (PTZ) de las cámaras ópticas remotas."""
    return {
        "status": "success",
        "pan": payload.get("pan", 0.0),
        "tilt": payload.get("tilt", 0.0),
        "zoom": payload.get("zoom", 1.0),
        "message": "PTZ optics adjusted successfully."
    }
