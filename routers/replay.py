from fastapi import APIRouter

router = APIRouter(prefix="/api/replay", tags=["Telemetry Replay Scrubber"])

@router.post("/seek")
def seek_telemetry_replay(payload: dict):
    """Permite retroceder o avanzar en el tiempo sobre las sesiones de vuelo grabadas."""
    target_time = payload.get("timestamp", 1793149920)
    speed = payload.get("speed", 1.0)
    return {
        "status": "success",
        "replay_state": "PLAYING",
        "current_seek_timestamp": target_time,
        "playback_speed": f"{speed}x",
        "message": f"Telemetry scrubbed to timestamp {target_time} at {speed}x speed."
    }
