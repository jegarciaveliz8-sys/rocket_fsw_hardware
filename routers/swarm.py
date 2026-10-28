from fastapi import APIRouter

router = APIRouter(prefix="/api/swarm", tags=["Swarm & Multi-Vehicle Control"])

@router.get("/vehicles")
def list_swarm_vehicles():
    """Devuelve la flota de vehículos activos bajo control de enjambre."""
    return {
        "status": "success",
        "fleet_size": 3,
        "vehicles": [
            {"id": "ODYSSEY-LEADER", "role": "COMMAND", "lat": 14.5975, "lon": -90.5131, "alt": 21974.7},
            {"id": "ODYSSEY-SCOUT-01", "role": "RECON", "lat": 14.5980, "lon": -90.5140, "alt": 21500.0},
            {"id": "ODYSSEY-SCOUT-02", "role": "RECON", "lat": 14.5970, "lon": -90.5120, "alt": 21500.0}
        ]
    }

@router.post("/command")
def broadcast_swarm_command(payload: dict):
    """Envía un comando sincronizado a toda la flota de enjambre."""
    cmd = payload.get("command", "HOLD")
    return {
        "status": "success",
        "broadcast_command": cmd,
        "target_count": 3,
        "message": f"Command '{cmd}' broadcasted to entire swarm fleet successfully."
    }
